"""Shared, versioned binary vectors for the Python and standalone Rust runners."""

from contextlib import ExitStack
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest

from tools.runner import arguments, execute, require, run_checks


@dataclass(frozen=True)
class VectorCase:
    id: str
    name: str
    argv: tuple[str, ...]
    input: bytes
    expected: bytes | None
    rejected: bool
    input_file: bool
    io: str
    stderr: bytes | None
    roundtrip_argv: tuple[str, ...] | None


def _hex(value):
    if not isinstance(value, str) or not re.fullmatch(r"(?:[0-9a-f]{2})*", value):
        raise ValueError("bytes devem usar hexadecimal minúsculo, sem espaços")
    return bytes.fromhex(value)


def load_cases(path):
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(document, dict) or set(document) != {"schema_version", "cases"}
            or type(document["schema_version"]) is not int or document["schema_version"] != 1
            or not isinstance(document["cases"], list) or not document["cases"]):
        raise ValueError("esperado schema_version: 1 e lista não vazia de cases")
    cases, identifiers = [], set()
    required = {"id", "name", "argv", "stdin_hex"}
    allowed = required | {"stdout_hex", "reject", "input_file", "io", "stderr_hex", "roundtrip_argv"}
    for raw in document["cases"]:
        if not isinstance(raw, dict) or not required <= raw.keys() or raw.keys() - allowed:
            raise ValueError("campos inválidos no caso de teste")
        identifier = raw["id"]
        if (not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier)
                or identifier in identifiers):
            raise ValueError(f"ID de caso inválido ou duplicado: {identifier}")
        identifiers.add(identifier)
        if not isinstance(raw["name"], str) or not raw["name"].strip():
            raise ValueError(f"{identifier}: name deve ser texto não vazio")
        argv = raw["argv"]
        if (not isinstance(argv, list)
                or any(not isinstance(arg, str) or "\0" in arg for arg in argv)):
            raise ValueError(f"{identifier}: argv inválido")
        rejected = raw.get("reject", False)
        input_file = raw.get("input_file", False)
        if type(rejected) is not bool or type(input_file) is not bool:
            raise ValueError(f"{identifier}: reject e input_file devem ser booleanos")
        if rejected == ("stdout_hex" in raw):
            raise ValueError(f"{identifier}: use stdout_hex OU reject:true")
        io = raw.get("io", "normal")
        if io not in ("normal", "full", "directory", "broken_pipe"):
            raise ValueError(f"{identifier}: modo io inválido")
        if input_file != ("{input}" in argv) or (input_file and io != "normal"):
            raise ValueError(f"{identifier}: input_file exige argv com {{input}} e io normal")
        roundtrip = raw.get("roundtrip_argv")
        if "roundtrip_argv" in raw:
            if (not isinstance(roundtrip, list) or not roundtrip
                    or any(not isinstance(arg, str) or "\0" in arg or arg == "{input}"
                           for arg in roundtrip)
                    or rejected or input_file or io != "normal"):
                raise ValueError(f"{identifier}: roundtrip_argv exige argumentos válidos, stdout_hex e io normal sem arquivo")
        cases.append(VectorCase(
            identifier, raw["name"], tuple(argv), _hex(raw["stdin_hex"]),
            None if rejected else _hex(raw["stdout_hex"]), rejected, input_file, io,
            _hex(raw["stderr_hex"]) if "stderr_hex" in raw else None,
            tuple(roundtrip) if roundtrip is not None else None,
        ))
    return cases


def compare_output(expected, actual):
    if expected == actual:
        return
    message = f"Saída diferente: esperado {expected[:128]!r}; recebido {actual[:128]!r}"
    # P6 diagnostics are inferred from the expected image, never candidate data.
    # Other binary formats keep the ordinary byte comparison.
    header = re.match(rb"P6\n([0-9]+) ([0-9]+)\n255\n", expected[:128])
    if header:
        width, height = map(int, header.groups())
        start = header.end()
        if width > 0 and height > 0 and len(expected) - start == width * height * 3:
            offset = next((i for i, pair in enumerate(zip(expected, actual))
                           if pair[0] != pair[1]), None)
            if offset is not None and offset >= start:
                pixel, channel = divmod(offset - start, 3)
                message += f"\nPixel ({pixel % width}, {pixel // width}), channel {'RGB'[channel]}"
    raise AssertionError(message)


def check_case(case, program, timeout):
    with ExitStack() as stack:
        data, argv = case.input, case.argv
        options = {}
        if case.input_file:
            directory = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="oxide-test-")))
            path = directory / "input with spaces.bin"
            path.write_bytes(data)
            argv = tuple(str(path) if arg == "{input}" else arg for arg in argv)
            data = b""
        if case.io == "full":
            if not Path("/dev/full").exists():
                raise unittest.SkipTest("/dev/full indisponível")
            options["output"] = stack.enter_context(open("/dev/full", "wb", buffering=0))
        elif case.io == "directory":
            if not sys.platform.startswith("linux"):
                raise unittest.SkipTest("stdin de diretório requer Linux")
            fd = os.open("/", os.O_RDONLY)
            stack.callback(os.close, fd)
            options["input_stream"] = fd
        elif case.io == "broken_pipe":
            reader, writer = os.pipe()
            os.close(reader)
            options["output"] = stack.enter_context(os.fdopen(writer, "wb", buffering=0))
        result = execute(program, data, argv=argv, timeout=timeout,
                         limit=262144 if case.rejected else len(case.expected), **options)
        if case.rejected:
            require(result.returncode != 0, "Entrada inválida ou erro de E/S retornou sucesso")
            require(bool(result.stderr.strip()), "Erro sem diagnóstico em stderr")
        else:
            require(result.returncode == 0,
                    f"Status {result.returncode}; stderr: {result.stderr[:512]!r}")
            compare_output(case.expected, result.stdout)
        if case.stderr is not None:
            require(result.stderr == case.stderr,
                    f"stderr diferente: esperado {case.stderr[:128]!r}; recebido {result.stderr[:128]!r}")
        if case.roundtrip_argv is not None:
            decoded = execute(program, result.stdout, argv=case.roundtrip_argv,
                              timeout=timeout, limit=len(case.input))
            require(decoded.returncode == 0,
                    f"Status {decoded.returncode} na volta; stderr: {decoded.stderr[:512]!r}")
            compare_output(case.input, decoded.stdout)


def main(path):
    args = arguments()
    try:
        cases = load_cases(path)
    except (ValueError, OSError) as error:
        print(f"Suíte inválida: {error}", file=sys.stderr)
        return 2
    return run_checks([(f"{case.id}: {case.name}",
                        lambda case=case: check_case(case, args.program, args.timeout))
                       for case in cases])
