#!/usr/bin/env python3
"""Contrato público de 002-ppm, incluindo erros de escrita."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.runner import arguments, execute, require, run_checks

HEADER = b"P6\n256 256\n255\n"
SIZE = 196623


def main():
    args = arguments()

    def image():
        result = execute(args.program, timeout=args.timeout, limit=SIZE)
        require(result.returncode == 0,
                f"Status {result.returncode}; stderr: {result.stderr!r}")
        require(result.stdout.startswith(HEADER), "Cabeçalho P6 incorreto")
        require(len(result.stdout) == SIZE,
                f"Tamanho esperado: {SIZE}; recebido: {len(result.stdout)} (ou mais)")
        for offset in range(15, SIZE, 3):
            y, x = divmod((offset - 15) // 3, 256)
            actual = tuple(result.stdout[offset:offset + 3])
            require(actual == (x, y, 0),
                    f"Pixel ({x}, {y}): esperado {(x, y, 0)}, recebido {actual}")

    def write_error():
        if not Path("/dev/full").exists():
            raise unittest.SkipTest("/dev/full indisponível neste sistema")
        with open("/dev/full", "wb", buffering=0) as full:
            result = execute(args.program, timeout=args.timeout, output=full)
        require(result.returncode != 0, "Erro de escrita retornou sucesso")
        require(bool(result.stderr.strip()), "Erro de escrita sem diagnóstico em stderr")

    return run_checks([
        ("cabeçalho, tamanho e todos os pixels", image),
        ("erro de escrita (/dev/full)", write_error),
    ])


if __name__ == "__main__":
    sys.exit(main())
