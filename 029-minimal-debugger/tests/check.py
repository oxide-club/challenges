#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import argparse, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("--prepare", action="store_true")
p.add_argument("candidate", nargs="?")
a = p.parse_args()
if a.prepare:
    subprocess.run(["make", "-C", str(ROOT), "all"], check=True)
    subprocess.run([sys.executable, str(ROOT / "tests/setup_controls.py")], check=True)
    for name, typ in [("arith-exec", "EXEC"), ("arith-pie", "DYN")]:
        h = subprocess.check_output(
            ["readelf", "-h", str(ROOT / "build" / name)], text=True
        )
        assert typ in h, (name, typ)
        h = subprocess.check_output(
            ["readelf", "-l", str(ROOT / "build" / name)], text=True
        )
        assert "INTERP" not in h, name
    r = subprocess.run(
        [str(ROOT / "build/oxdbg"), "--", str(ROOT / "build/arith-exec")],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 1 and "não implementado" in r.stderr
    print(
        "PASS alvos ET_EXEC/PIE sem INTERP e starter incompleto; probe e solução são verificações separadas"
    )
elif a.candidate:
    probe = subprocess.run(
        [str(ROOT / "build/probe")], capture_output=True, text=True, timeout=9
    )
    if probe.returncode == 77:
        print(
            "NOT_RUN: ptrace indisponível, probe independente: " + probe.stderr.strip(),
            file=sys.stderr,
        )
        sys.exit(77)
    if probe.returncode != 0:
        print("FAIL probe independente: " + probe.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    for script in ["test.py", "lifecycle.py", "unavailable.py"]:
        status = subprocess.run(
            [sys.executable, str(ROOT / "tests" / script), a.candidate]
        ).returncode
        if status:
            sys.exit(status)
else:
    p.error("use --prepare ou caminho do oxdbg")
