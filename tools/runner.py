"""Shared CLI and process handling; challenge assertions live beside each spec."""

import argparse
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time
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
    """Bound output during execution, while feeding stdin without pipe deadlocks."""
    try:
        process = subprocess.Popen(
            [str(program)], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE if output is None else output,
            stderr=subprocess.PIPE, start_new_session=True, bufsize=0,
        )
    except OSError as error:
        raise AssertionError(f"Não foi possível iniciar o executável: {error}") from error

    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    caps = {"stdout": limit, "stderr": 65536}
    deadline = time.monotonic() + timeout
    position = 0
    try:
        with selectors.DefaultSelector() as selector:
            def register(stream, event, name):
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, event, name)

            def close(stream):
                selector.unregister(stream)
                stream.close()

            if data:
                register(process.stdin, selectors.EVENT_WRITE, "stdin")
            else:
                process.stdin.close()
            if process.stdout is not None:
                register(process.stdout, selectors.EVENT_READ, "stdout")
            register(process.stderr, selectors.EVENT_READ, "stderr")

            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(str(program), timeout)
                for key, _ in selector.select(remaining):
                    stream, name = key.fileobj, key.data
                    if name == "stdin":
                        try:
                            position += os.write(stream.fileno(), data[position:position + 65536])
                        except BrokenPipeError:
                            close(stream)
                            continue
                        except BlockingIOError:
                            continue
                        if position == len(data):
                            close(stream)
                    else:
                        # Read at most one byte beyond the cap to detect overflow.
                        size = min(65536, caps[name] - len(buffers[name]) + 1)
                        try:
                            chunk = os.read(stream.fileno(), size)
                        except BlockingIOError:
                            continue
                        if not chunk:
                            close(stream)
                            continue
                        buffers[name].extend(chunk)
                        require(len(buffers[name]) <= caps[name],
                                f"Limite de saída excedido ({name}: {caps[name]} bytes)")

            # A candidate may close both streams and still keep running.
            process.wait(timeout=max(0, deadline - time.monotonic()))
        return subprocess.CompletedProcess(
            [str(program)], process.returncode,
            bytes(buffers["stdout"]), bytes(buffers["stderr"]),
        )
    except BaseException as error:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        if isinstance(error, subprocess.TimeoutExpired):
            raise AssertionError(f"Limite de tempo excedido ({timeout:g} s)") from None
        raise
    finally:
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                stream.close()


def run_checks(checks):
    suite = unittest.TestSuite(
        unittest.FunctionTestCase(check, description=name) for name, check in checks
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1
