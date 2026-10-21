"""Generate binary samples and vectors from the format, without a solution import."""
from itertools import groupby
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def canonical(data):
    result = bytearray()
    for value, group in groupby(data):
        count = sum(1 for _ in group)
        while count:
            chunk = min(255, count)
            result.extend((chunk, value))
            count -= chunk
    return bytes(result)


def main():
    cases = []

    def exact(identifier, name, data, expected, argv, **extra):
        cases.append(dict(id=identifier, name=name, argv=argv, stdin_hex=data.hex(), stdout_hex=expected.hex(), **extra))

    def reject(identifier, name, data, argv, io="normal"):
        cases.append(dict(id=identifier, name=name, argv=argv, stdin_hex=data.hex(), reject=True, io=io))

    vectors = [
        ("empty", b"", b""), ("single", b"A", b"\x01A"),
        ("triple", b"AAA", b"\x03A"), ("mixed", b"AAAAABBBCC", b"\x05A\x03B\x02C"),
        ("alternating", b"ABAB", b"\x01A\x01B\x01A\x01B"),
        ("run-255", b"A" * 255, b"\xffA"), ("run-256", b"A" * 256, b"\xffA\x01A"),
        ("run-510", b"A" * 510, b"\xffA\xffA"),
        ("run-511", b"A" * 511 + b"B", b"\xffA\xffA\x01A\x01B"),
        ("binary", b"\0\0\xff", b"\x02\0\x01\xff"),
        ("all-bytes", bytes(range(256)), bytes(v for n in range(256) for v in (1, n))),
        ("run-65536", bytes(65536), b"\xff\0" * 257 + b"\x01\0"),
    ]
    for identifier, original, encoded in vectors:
        assert canonical(original) == encoded
        (HERE / (identifier + ".bin")).write_bytes(original)
        (HERE / (identifier + ".rle")).write_bytes(encoded)
        exact("encode-" + identifier, "Encode " + identifier, original, encoded, ["encode"])
        exact("decode-" + identifier, "Decode " + identifier, encoded, original, ["decode"])
    exact("decode-adjacent", "Adjacent equal values", b"\x01A\x02A\xffA\x01A", b"A" * 259, ["decode"])
    exact("decode-all-counts", "Every valid count", bytes(v for n in range(1, 256) for v in (n, 255)), b"\xff" * 32640, ["decode"])
    for identifier, data in [("zero-count", b"\0A"), ("incomplete", b"\x03"), ("zero-incomplete", b"\0"), ("incomplete-after-prefix", b"\x01A\x03"), ("zero-after-prefix", b"\x01A\0B")]:
        reject("decode-" + identifier, "Reject " + identifier, data, ["decode"])
    for identifier, argv in [("missing", []), ("uppercase", ["ENCODE"]), ("empty", [""]), ("unknown", ["other"]), ("encode-extra", ["encode", "extra"]), ("decode-extra", ["decode", "extra"])]:
        reject("args-" + identifier, "Reject " + identifier + " argument", b"", argv)
    state = 3
    mask = (1 << 64) - 1
    for size in (0, 1, 254, 255, 256, 8191, 8192, 8193, 131072):
        data = bytearray()
        for _ in range(size):
            state ^= (state << 13) & mask
            state ^= state >> 7
            state ^= (state << 17) & mask
            data.append(state & 255)
        exact("roundtrip-" + str(size), "Round trip " + str(size) + " deterministic bytes", data, canonical(data), ["encode"], roundtrip_argv=["decode"])
    for mode, small, large in [("encode", b"A", bytes(range(256)) * 1024), ("decode", b"\x01A", b"\xffA" * 1024)]:
        for label, data in [("small", small), ("large", large)]:
            reject(mode + "-write-" + label, mode + ": /dev/full, " + label + " input", data, [mode], "full")
        reject(mode + "-read-error", mode + ": directory stdin", b"", [mode], "directory")
        reject(mode + "-broken-pipe", mode + ": pipe without reader", small, [mode], "broken_pipe")
    assert len(cases) == 54
    (HERE.parent / "tests/cases.json").write_text(json.dumps(dict(schema_version=1, cases=cases), indent=2) + "\n")


if __name__ == "__main__":
    import argparse
    import tempfile

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare regenerated artifacts without changing files")
    args = parser.parse_args()
    if args.check:
        original = HERE
        with tempfile.TemporaryDirectory(prefix="oxide-vectors-") as temporary:
            HERE = Path(temporary) / "materials"
            HERE.mkdir()
            (HERE.parent / "tests").mkdir()
            main()
            for generated in HERE.parent.rglob("*"):
                if generated.is_file():
                    committed = original.parent / generated.relative_to(HERE.parent)
                    if not committed.is_file() or committed.read_bytes() != generated.read_bytes():
                        parser.exit(1, f"Outdated artifact: {committed}\n")
        print("Generated artifacts are current")
    else:
        main()
