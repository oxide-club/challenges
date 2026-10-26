#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verificações públicas da biblioteca; --prepare valida a preparação do pacote."""
import argparse, pathlib, subprocess, sys

p = argparse.ArgumentParser()
p.add_argument("--prepare", action="store_true")
args = p.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
commands = (
    [
        ["cargo", "check", "--offline"],
        ["cargo", "test", "--offline", "--no-run"],
        [sys.executable, "tests/compile.py"],
    ]
    if args.prepare
    else [["cargo", "test", "--offline"], [sys.executable, "tests/compile.py"]]
)
if args.prepare and (root / "tests/support_contract.rs").exists():
    commands.append(["cargo", "test", "--offline", "--test", "support_contract"])
for cmd in commands:
    print("+", " ".join(cmd), flush=True)
    try:
        result = subprocess.run(cmd, cwd=root, timeout=120)
    except FileNotFoundError as e:
        print("INDISPONÍVEL:", e)
        sys.exit(77)
    except subprocess.TimeoutExpired:
        print("FALHOU: tempo excedido")
        sys.exit(1)
    if result.returncode:
        sys.exit(1)
print(
    "APROVADO: preparação; núcleo ainda deve ser implementado."
    if args.prepare
    else "APROVADO: testes públicos; revisão de invariantes continua obrigatória."
)
