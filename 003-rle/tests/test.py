#!/usr/bin/env python3
"""Contrato binário de 003-rle; somente biblioteca padrão."""

import os
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.runner import arguments, execute, require, run_checks


VECTORS = [
    (b"", b""),
    (b"A", b"\x01A"),
    (b"AAA", b"\x03A"),
    (b"AAAAABBBCC", b"\x05A\x03B\x02C"),
    (b"ABAB", b"\x01A\x01B\x01A\x01B"),
    (b"A" * 255, b"\xffA"),
    (b"A" * 256, b"\xffA\x01A"),
    (b"A" * 510, b"\xffA\xffA"),
    (b"A" * 511 + b"B", b"\xffA\xffA\x01A\x01B"),
    (b"\x00\x00\xff", b"\x02\x00\x01\xff"),
    (bytes(range(256)), b"".join(bytes((1, n)) for n in range(256))),
    (b"\x00" * 65536, b"\xff\x00" * 257 + b"\x01\x00"),
]


def main():
    args = arguments()

    def run(mode, data, **kwargs):
        return execute(args.program, data, argv=(mode,),
                       timeout=args.timeout, **kwargs)

    def successful(mode, data, expected):
        result = run(mode, data, limit=len(expected))
        require(result.returncode == 0,
                f"{mode}: status {result.returncode}; stderr: {result.stderr!r}")
        require(result.stdout == expected, f"{mode}: bytes diferentes do esperado")

    def rejected(result):
        require(result.returncode != 0, "Entrada inválida ou erro de E/S retornou sucesso")
        require(bool(result.stderr.strip()), "Erro sem diagnóstico em stderr")

    def vectors():
        for original, encoded in VECTORS:
            successful("encode", original, encoded)
            successful("decode", encoded, original)

    def adjacent():
        successful("decode", b"\x01A\x02A\xffA\x01A", b"A" * 259)
        # Todo valor de contagem válido, não apenas aqueles emitidos pelos exemplos.
        successful("decode", b"".join(bytes((n, 0xff)) for n in range(1, 256)),
                   b"\xff" * 32640)

    def invalid():
        for data in (b"\x00A", b"\x03", b"\x00", b"\x01A\x03",
                     b"\x01A\x00B"):
            rejected(run("decode", data))
        for argv in ((), ("ENCODE",), ("",), ("other",),
                     ("encode", "extra"), ("decode", "extra")):
            rejected(execute(args.program, argv=argv, timeout=args.timeout))

    def round_trips():
        rng = random.Random(3)
        for size in (0, 1, 254, 255, 256, 8191, 8192, 8193, 131072):
            original = bytes(rng.randrange(256) for _ in range(size))
            encoded = run("encode", original, limit=2 * size)
            require(encoded.returncode == 0, f"encode falhou: {encoded.stderr!r}")
            require(len(encoded.stdout) % 2 == 0, "encode produziu par incompleto")
            # Oráculo independente impede que dois modos com o mesmo erro
            # de formato passem apenas por conseguirem inverter um ao outro.
            pairs = list(zip(encoded.stdout[::2], encoded.stdout[1::2]))
            require(all(count for count, _ in pairs), "encode produziu contagem zero")
            require(b"".join(bytes((value,)) * count for count, value in pairs)
                    == original, "encode não preservou os bytes")
            require(all(value != next_value or count == 255
                        for (count, value), (_, next_value) in zip(pairs, pairs[1:])),
                    "encode dividiu uma sequência antes de 255")
            successful("decode", encoded.stdout, original)

    def write_errors():
        if not Path("/dev/full").exists():
            raise unittest.SkipTest("/dev/full indisponível")
        for mode, data in (("encode", b"A"), ("decode", b"\x01A"),
                           ("encode", bytes(range(256)) * 1024),
                           ("decode", b"\xffA" * 1024)):
            with open("/dev/full", "wb", buffering=0) as full:
                rejected(run(mode, data, output=full))

    def read_errors():
        if not sys.platform.startswith("linux"):
            raise unittest.SkipTest("stdin de diretório requer Linux")
        descriptor = os.open(Path(__file__).parent, os.O_RDONLY)
        try:
            for mode in ("encode", "decode"):
                rejected(run(mode, b"", input_stream=descriptor))
        finally:
            os.close(descriptor)

    def broken_pipe():
        for mode, data in (("encode", b"A"), ("decode", b"\x01A")):
            reader, writer = os.pipe()
            os.close(reader)
            with os.fdopen(writer, "wb", buffering=0) as output:
                rejected(run(mode, data, output=output))

    return run_checks([
        ("vetores exatos, bytes binários e sequências longas", vectors),
        ("pares adjacentes e todas as contagens válidas", adjacent),
        ("argumentos, contagem zero e pares incompletos", invalid),
        ("ida e volta aleatória com semente fixa", round_trips),
        ("erro de escrita, inclusive no flush (/dev/full)", write_errors),
        ("erro de leitura (stdin de diretório)", read_errors),
        ("erro de escrita (pipe sem leitor)", broken_pipe),
    ])


if __name__ == "__main__":
    sys.exit(main())
