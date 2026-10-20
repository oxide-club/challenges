"""Shared CLI and process handling; challenge assertions live beside each spec."""

import argparse
import math
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest


def arguments():
    parser = argparse.ArgumentParser(description="Testes públicos do Oxide Club")
    parser.add_argument("program", help="caminho do executável a testar")

    def positive_seconds(value):
        number = float(value)
        if not math.isfinite(number) or number <= 0:
            raise argparse.ArgumentTypeError("timeout deve ser positivo e finito")
        return number

    parser.add_argument("--timeout", type=positive_seconds, default=5.0,
                        help="limite por caso em segundos (padrão: 5)")
    args = parser.parse_args()
    args.program = Path(args.program).resolve()
    if not args.program.is_file() or not os.access(args.program, os.X_OK):
        parser.error(f"executável ausente ou sem permissão: {args.program}")
    return args


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def execute(program, data=b"", *, timeout=5, output=None, limit=262144):
    """Capture bounded diagnostics; isolate the process group for timeout cleanup."""
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            process = subprocess.Popen(
                [str(program)], stdin=subprocess.PIPE,
                stdout=stdout if output is None else output, stderr=stderr,
                start_new_session=True,
            )
        except OSError as error:
            raise AssertionError(f"Não foi possível iniciar o executável: {error}") from error
        try:
            process.communicate(input=data, timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            raise AssertionError(f"Limite de tempo excedido ({timeout:g} s)") from None
        stdout.seek(0)
        stderr.seek(0)
        return subprocess.CompletedProcess(
            [str(program)], process.returncode,
            stdout.read(limit + 1), stderr.read(4096),
        )


def run_checks(checks):
    suite = unittest.TestSuite(
        unittest.FunctionTestCase(check, description=name) for name, check in checks
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1
