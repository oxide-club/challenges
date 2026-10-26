#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import argparse, ctypes, json, os, pathlib, queue, signal, subprocess, tempfile, threading, time

ROOT = pathlib.Path(__file__).resolve().parents[1]


def verify(candidate):
    candidate = str(pathlib.Path(candidate).resolve())
    with tempfile.TemporaryDirectory(prefix="ox-eintr-") as d:
        lib = pathlib.Path(d) / "eintr.so"
        witness = pathlib.Path(d) / "witness"
        subprocess.run(
            [
                "cc",
                "-shared",
                "-fPIC",
                str(ROOT / "tests/eintr.c"),
                "-ldl",
                "-o",
                str(lib),
            ],
            check=True,
        )
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(lib)
        env["OX_EINTR_WITNESS"] = str(witness)
        p = subprocess.run(
            [candidate, "--", str(ROOT / "build/arith-exec")],
            input="run\ncontinue\n",
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
        )
        assert witness.read_text() == "EINTR\n", "injeção não executada"
        assert p.returncode == 0, (
            "falha após EINTR injetado em waitpid",
            p.returncode,
            p.stderr,
        )
        rows = [json.loads(x) for x in p.stdout.splitlines()]
        assert any(r.get("exit_code") == 7 for r in rows), "EINTR perdeu execução"
        for pid in {r["pid"] for r in rows if r["pid"] > 0}:
            assert not pathlib.Path("/proc", str(pid)).exists(), "filho após EINTR"
        print("PASS EINTR injetado em waitpid e child reaping")
    libc = ctypes.CDLL(None, use_errno=True)
    assert libc.prctl(36, 1, 0, 0, 0) == 0, "subreaper"
    p = None
    child = None
    try:
        p = subprocess.Popen(
            [candidate, "--", str(ROOT / "build/arith-exec")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        events = queue.Queue()

        def reader():
            for line in p.stdout:
                events.put(json.loads(line))
            events.put(None)

        threading.Thread(target=reader, daemon=True).start()
        p.stdin.write("run\n")
        p.stdin.flush()
        end = time.monotonic() + 5
        while time.monotonic() < end:
            r = events.get(timeout=max(0.01, end - time.monotonic()))
            assert r, "EOF antes de exec"
            if r["cause"] == "exec":
                child = r["pid"]
                break
        assert child and child != p.pid, "evento exec não identificou tracee"
        status = pathlib.Path("/proc", str(child), "status").read_text()
        assert f"PPid:\t{p.pid}\n" in status, "PID não é filho do tracer"
        p.kill()
        p.wait(timeout=3)
        end = time.monotonic() + 3
        while time.monotonic() < end:
            got, st = os.waitpid(child, os.WNOHANG)
            if got:
                assert os.WIFSIGNALED(st) and os.WTERMSIG(st) == signal.SIGKILL, (
                    "EXITKILL não encerrou tracee com SIGKILL",
                    st,
                )
                child = None
                break
            time.sleep(0.01)
        assert child is None, "tracee sobreviveu ao tracer"
        print("PASS EXITKILL e child reaping pelo supervisor após morte do tracer")
    finally:
        if p and p.poll() is None:
            p.kill()
            p.wait()
        if child:
            try:
                os.kill(child, signal.SIGKILL)
                os.waitpid(child, 0)
            except ProcessLookupError:
                pass
            except ChildProcessError:
                pass
        libc.prctl(36, 0, 0, 0, 0)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("candidate")
    a = p.parse_args()
    try:
        verify(a.candidate)
    except (
        AssertionError,
        OSError,
        ValueError,
        queue.Empty,
        subprocess.SubprocessError,
    ) as e:
        p.exit(1, "FAIL " + str(e) + "\n")
