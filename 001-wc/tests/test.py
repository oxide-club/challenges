#!/usr/bin/env python3
"""Contrato público de 001-wc. Nenhuma extensão opcional é exigida."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.runner import arguments, execute, require, run_checks

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def cases():
    for path in sorted(FIXTURES.glob("*.in")):
        yield path.stem, path.read_bytes(), path.with_suffix(".out").read_bytes()
    yield "palavra-longa", b"x" * 131072, b"0 1 131072\n"
    yield "muitas-linhas", b"a b\n" * 32768, b"32768 65536 131072\n"


def main():
    args = arguments()
    checks = []
    for name, data, expected in cases():
        def check(data=data, expected=expected):
            result = execute(args.program, data, timeout=args.timeout, limit=1024)
            require(result.returncode == 0,
                    f"Status {result.returncode}; stderr: {result.stderr!r}")
            require(result.stdout == expected,
                    f"Esperado {expected!r}; recebido {result.stdout[:120]!r}")
        checks.append((name, check))
    require(len(checks) >= 3, "Fixtures ausentes")
    return run_checks(checks)


if __name__ == "__main__":
    sys.exit(main())
