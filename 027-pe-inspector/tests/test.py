# SPDX-License-Identifier: MIT
import sys

sys.dont_write_bytecode = True
"""Entrada convencional para executar a suíte pública sobre um programa."""
import argparse
from pathlib import Path
from check import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("program", type=Path)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.program.resolve()) else 1)
