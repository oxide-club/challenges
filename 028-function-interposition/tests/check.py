#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import argparse, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("--prepare", action="store_true")
p.add_argument("directory", nargs="?")
a = p.parse_args()
if a.prepare:
    subprocess.run(["make", "-C", str(ROOT), "all"], check=True)
    r = subprocess.run(
        [sys.executable, str(ROOT / "tests/test.py"), str(ROOT / "build")],
        capture_output=True,
        text=True,
    )
    if r.returncode != 1 or "'API'" not in r.stderr:
        sys.exit("FAIL starter não falhou pelo contrato incompleto")
    print("PASS build e falha intencional API do starter; não aprova solução")
elif a.directory:
    sys.exit(
        subprocess.run(
            [sys.executable, str(ROOT / "tests/test.py"), a.directory]
        ).returncode
    )
else:
    p.error("use --prepare ou diretório com app/direct/libcalc.so/libtrace.so")
