#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import argparse, json, pathlib, subprocess, os, signal, tempfile, shutil, ctypes, queue, threading

ROOT = pathlib.Path(__file__).resolve().parents[1]


def session(candidate, target, commands, args=(), status=0):
    p = subprocess.run(
        [str(candidate), "--", str(target), *args],
        input=commands,
        text=True,
        capture_output=True,
        timeout=9,
    )
    assert p.returncode == status, ("status", p.returncode, status, p.stderr)
    rows = [json.loads(x) for x in p.stdout.splitlines()]
    assert rows and [r["seq"] for r in rows] == list(
        range(1, len(rows) + 1)
    ), "sequência dos eventos"
    for r in rows:
        assert r["state"] in [
            "NEW",
            "STARTING",
            "STOPPED",
            "RUNNING",
            "EXITED",
            "FAILED",
        ]
        assert isinstance(r["pid"], int) and isinstance(r["cause"], str)
        for key in ["signal", "term_signal"]:
            if key in r:
                assert type(r[key]) is int, ("tipo inteiro", key)
        if r["cause"] in [
            "exec",
            "step",
            "signal_step",
            "signal_delivery",
            "unsupported_stop",
        ]:
            assert all(k in r for k in ["raw_status", "signal", "event", "siginfo"])
    for pid in {r["pid"] for r in rows if r["pid"] > 0}:
        assert not pathlib.Path("/proc", str(pid)).exists(), (
            "filho não recolhido",
            pid,
        )
    return rows


def pending_trap_during_step(candidate, target):
    p = subprocess.Popen(
        [str(candidate), "--", str(target)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    events = queue.Queue()
    rows = []

    def reader():
        for line in p.stdout:
            events.put(json.loads(line))
        events.put(None)

    threading.Thread(target=reader, daemon=True).start()
    try:
        p.stdin.write("run\nregs\n")
        p.stdin.flush()
        while True:
            r = events.get(timeout=9)
            assert r is not None, "EOF antes do alvo STOPPED"
            rows.append(r)
            if r["cause"] == "regs":
                break
        child = r["pid"]
        assert child > 0 and r["state"] == "STOPPED"
        assert (
            f"PPid:\t{p.pid}\n"
            in pathlib.Path("/proc", str(child), "status").read_text()
        ), "PID não é filho do tracer"
        # Linux x86-64: tgkill entrega SI_TKILL enquanto o filho está parado.
        libc = ctypes.CDLL(None, use_errno=True)
        assert (
            libc.syscall(234, child, child, signal.SIGTRAP) == 0
        ), "tgkill do supervisor falhou"
        p.stdin.write("step\ncontinue\n")
        p.stdin.close()
        while True:
            r = events.get(timeout=9)
            if r is None:
                break
            rows.append(r)
        assert p.wait(timeout=9) == 0, "falha ao retomar alvo com SIGTRAP pendente"
        assert any(
            r["cause"] == "signal_delivery"
            and r.get("signal") == signal.SIGTRAP
            and r.get("siginfo", {}).get("code") == -6
            for r in rows
        ), "SIGTRAP SI_TKILL durante step foi apagado"
        assert any(
            r.get("term_signal") == signal.SIGTRAP for r in rows if r["cause"] == "exit"
        ), "SIGTRAP SI_TKILL não foi reinjetado"
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()


def check(candidate):
    candidate = pathlib.Path(candidate).resolve()
    b = ROOT / "build"
    for name in ["arith-exec", "arith-pie"]:
        rows = session(
            candidate,
            b / name,
            "regs\nrun\nrun\nstep\nregs\nstep\nregs\nstep\nregs\ncontinue\nregs\n",
        )
        regs = [r["regs"] for r in rows if r["cause"] == "regs"]
        assert len(regs) == 3, "três snapshots"
        for r in regs:
            for k in ["RIP", "RSP", "RAX", "RBX", "RCX", "RDX", "RFLAGS"]:
                assert r[k].startswith("0x") and int(r[k], 16) >= 0
        assert [int(r["RAX"], 16) for r in regs] == [5, 8, 8], "aritmética"
        assert int(regs[2]["RBX"], 16) == 8, "RBX"
        assert int(regs[1]["RIP"], 16) > int(regs[0]["RIP"], 16) and int(
            regs[2]["RIP"], 16
        ) > int(regs[1]["RIP"], 16), "progresso RIP"
        assert (
            len([r for r in rows if r["cause"] == "rejected"]) == 3
        ), "estados inválidos"
        assert any(r["cause"] == "exec" for r in rows), "exec event"
        assert any(
            r.get("exit_code") == 7 for r in rows if r["cause"] == "exit"
        ), "exit distinto de ferramenta"
    for mode, sig in [
        ("usr1", signal.SIGUSR1),
        ("trap", signal.SIGTRAP),
        ("term", signal.SIGTERM),
    ]:
        rows = session(candidate, b / "signals", "run\ncontinue\ncontinue\n", [mode])
        stops = [r for r in rows if r["cause"] == "signal_delivery"]
        assert len(stops) == 1 and stops[0]["signal"] == sig, ("sinal ordinário", mode)
        assert any(
            r.get("term_signal" if mode == "term" else "exit_code")
            == (sig if mode == "term" else 7)
            for r in rows
            if r["cause"] == "exit"
        ), ("entrega", mode)
    for mode, sig in [
        ("usr1", signal.SIGUSR1),
        ("trap", signal.SIGTRAP),
        ("term", signal.SIGTERM),
    ]:
        rows = session(
            candidate,
            b / "signals",
            "run\ncontinue\nstep\n" + ("continue\n" if mode != "term" else ""),
            [mode],
        )
        stops = [r for r in rows if r["cause"] == "signal_delivery"]
        assert len(stops) == 1 and stops[0]["signal"] == sig, (
            "sinal ordinário com step",
            mode,
        )
        assert any(
            r.get("term_signal" if mode == "term" else "exit_code")
            == (sig if mode == "term" else 7)
            for r in rows
            if r["cause"] == "exit"
        ), ("entrega com step", mode)
    rows = session(candidate, b / "signals", "run\ncontinue\ncontinue\n", ["group"], 1)
    assert any(r["cause"] == "unsupported_stop" for r in rows), "group stop"
    rows = session(
        candidate, b / "signals", "run\ncontinue\ncontinue\n", ["unknown-trap"]
    )
    assert any(
        r["cause"] == "signal_delivery" and r["signal"] == signal.SIGTRAP for r in rows
    ), "SIGTRAP do alvo deve ser signal-delivery-stop"
    assert any(
        r.get("term_signal") == signal.SIGTRAP for r in rows if r["cause"] == "exit"
    ), "SIGTRAP deve ser reinjetado"
    pending_trap_during_step(candidate, b / "arith-exec")
    rows = session(candidate, b / "step-trap", "run\n" + "step\n" * 32)
    assert any(
        r["cause"] == "signal_delivery" and r["signal"] == signal.SIGTRAP for r in rows
    ), "SIGTRAP do alvo durante step foi apagado"
    assert any(
        r.get("term_signal") == signal.SIGTRAP for r in rows if r["cause"] == "exit"
    ), "SIGTRAP durante step não foi reinjetado"
    with tempfile.TemporaryDirectory(prefix="ox-noexec-") as d:
        target = pathlib.Path(d) / "noexec"
        shutil.copyfile(b / "arith-exec", target)
        target.chmod(0o644)
        session(candidate, target, "run\n", status=1)
    session(candidate, b / "arith-exec", "run\nquit\n")
    session(candidate, b / "arith-exec", "run\n")
    session(candidate, b / "signals", "run\ncontinue\n", ["timeout"], 1)
    session(candidate, b / "does-not-exist", "run\n", status=1)
    print(
        "PASS ET_EXEC/PIE, estados, snapshots, sinais, EOF/quit, timeout e exec inválido"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("candidate")
    a = p.parse_args()
    try:
        check(a.candidate)
    except (
        AssertionError,
        ValueError,
        subprocess.TimeoutExpired,
        queue.Empty,
        OSError,
    ) as e:
        p.exit(1, "FAIL " + str(e) + "\n")
