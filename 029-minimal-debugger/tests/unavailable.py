#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Diferencie seccomp neutro, ptrace negado e falha funcional de exec."""
import errno, json, os, pathlib, subprocess, tempfile, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def kernel_records(path):
    assert path.is_file(), "testemunho do supervisor ausente"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    started = [r for r in rows if r.get("type") == "started"]
    assert (
        len(started) == 1
        and type(started[0]["candidate_pid"]) is int
        and started[0]["candidate_pid"] > 0
    ), "identidade do candidato no supervisor"
    assert not any(
        r.get("type") in ("orphan", "cleanup_timeout") for r in rows
    ), "filho pendente ao terminar candidato"
    candidate_pid = started[0]["candidate_pid"]
    attempts = [r for r in rows if r.get("type") == "denied" and r.get("request") == 0]
    assert any(
        r["ppid"] == candidate_pid and r["result"] == -1 and r["errno"] == errno.EPERM
        for r in attempts
    ), "tentativa de PTRACE_TRACEME do filho não observada no kernel"
    return candidate_pid, attempts


def check(candidate):
    candidate = str(pathlib.Path(candidate).resolve())
    probe = subprocess.run(
        [str(ROOT / "build/probe")], capture_output=True, text=True, timeout=9
    )
    if probe.returncode == 77:
        print("NOT_RUN: probe independente: " + probe.stderr.strip(), file=sys.stderr)
        return 77
    assert probe.returncode == 0, ("falha no probe independente", probe.stderr)
    with tempfile.TemporaryDirectory(prefix="ox-ptrace-denied-") as d:
        deny = str(pathlib.Path(d) / "deny")
        neutral = str(pathlib.Path(d) / "neutral")
        notifier = str(ROOT / "build/notify-ptrace")
        for source, output in [("deny_ptrace.c", deny), ("neutral_seccomp.c", neutral)]:
            subprocess.run(
                ["cc", str(ROOT / "tests" / source), "-o", output], check=True
            )
        probe = subprocess.run(
            [neutral, str(ROOT / "build/probe")],
            capture_output=True,
            text=True,
            timeout=9,
        )
        assert probe.returncode == 0, ("filtro neutro bloqueou ptrace", probe.stderr)
        p = subprocess.run(
            [neutral, candidate, "--", str(ROOT / "build/arith-exec")],
            input="run\ncontinue\n",
            capture_output=True,
            text=True,
            timeout=9,
        )
        assert p.returncode == 0, (
            "seccomp neutro não é indisponibilidade",
            p.returncode,
            p.stderr,
        )
        assert any(
            row.get("exit_code") == 7 for row in map(json.loads, p.stdout.splitlines())
        ), "filtro neutro deve executar alvo"
        probe = subprocess.run(
            [deny, str(ROOT / "build/probe")], capture_output=True, text=True, timeout=9
        )
        assert probe.returncode == 77 and "PTRACE_TRACEME" in probe.stderr, (
            "seccomp negador não comprovado",
            probe.stderr,
        )
        witness = pathlib.Path(d) / "probe-attempts.jsonl"
        proof = subprocess.run(
            [notifier, str(witness), str(ROOT / "build/probe")],
            capture_output=True,
            text=True,
            timeout=9,
        )
        if proof.returncode == 77 and not witness.exists():
            print(
                "NOT_RUN: supervisor de notificação indisponível: "
                + proof.stderr.strip(),
                file=sys.stderr,
            )
            return 77
        assert proof.returncode == 77, (
            "sonda independente do supervisor",
            proof.returncode,
            proof.stderr,
        )
        kernel_records(
            witness
        )  # O probe precisa provocar uma negação realmente observada.
        witness = pathlib.Path(d) / "candidate-attempts.jsonl"
        p = subprocess.Popen(
            [notifier, str(witness), candidate, "--", str(ROOT / "build/arith-exec")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            out, err = p.communicate("run\n", timeout=9)
        finally:
            if p.poll() is None:
                p.kill()
                p.wait()
        assert p.returncode == 77, (
            "bloqueio comprovado deve retornar 77",
            p.returncode,
            err,
        )
        rows = [json.loads(line) for line in out.splitlines()]
        records = [r for r in rows if r.get("cause") == "unavailable"]
        assert len(records) == 1, "evento estruturado unavailable ausente ou duplicado"
        r = records[0]
        assert (
            r.get("state") == "FAILED" and type(r.get("pid")) is int and r["pid"] > 0
        ), "pid real e estado FAILED obrigatórios"
        assert (
            r.get("operation") == "PTRACE_TRACEME"
            and type(r.get("errno")) is int
            and r["errno"] == errno.EPERM
        ), "operação/errno do bloqueio"
        assert r.get("evidence") == {
            "kind": "child_ptrace_result",
            "child_pid": r["pid"],
            "result": -1,
        }, "evidência estruturada do filho"
        candidate_pid, attempts = kernel_records(witness)
        assert any(
            a["pid"] == r["pid"]
            and a["ppid"] == candidate_pid
            and a["result"] == -1
            and a["errno"] == r["errno"]
            for a in attempts
        ), ("prova não corresponde à tentativa do filho", attempts)
        assert not pathlib.Path(
            "/proc", str(r["pid"])
        ).exists(), "filho não recolhido após indisponibilidade"
        assert (
            "PTRACE_TRACEME" in err and err.strip()
        ), "diagnóstico da operação ausente"
    print(
        "PASS indisponibilidade: filtro neutro, bloqueio real, notificação do kernel e evento estruturado"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(check(sys.argv[1]))
    except (AssertionError, subprocess.TimeoutExpired, OSError, ValueError) as e:
        sys.exit("FAIL " + str(e))
