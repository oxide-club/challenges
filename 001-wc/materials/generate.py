"""Rebuild the published WC byte samples and common runner vectors."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLES = {'bordas': ('20202061202062202020', '3020322031300a'), 'crlf': ('0d0a', '31203020320a'), 'duas-palavras': ('6120620a', '31203220340a'), 'espacos': ('6f6e6520202074776f0a', '3120322031300a'), 'exemplo': ('48656c6c6f20776f726c640a432069732066756e0a', '3220352032310a'), 'sem-quebra': ('68656c6c6f', '30203120350a'), 'separadores': ('20090a0d0b0c', '31203020360a'), 'todos-separadores': ('09616c7068610b626574610c67616d6d610d64656c746120657073696c6f6e0a', '3120352033320a'), 'ultima-linha': ('610a62', '31203220330a'), 'uma-linha': ('68656c6c6f0a', '31203120360a'), 'vazio': ('', '30203020300a')}


def main():
    cases = []
    for name, (input_hex, output_hex) in SAMPLES.items():
        data, expected = bytes.fromhex(input_hex), bytes.fromhex(output_hex)
        (HERE / (name + ".in")).write_bytes(data)
        (HERE / (name + ".out")).write_bytes(expected)
        cases.append(dict(id=name, name=name, argv=[], stdin_hex=input_hex, stdout_hex=output_hex))
    for name, label, data, expected in [
        ("palavra-longa", "128 KiB word", b"x" * 131072, b"0 1 131072\n"),
        ("muitas-linhas", "32768 lines", b"a b\n" * 32768, b"32768 65536 131072\n"),
    ]:
        cases.append(dict(id=name, name=label, argv=[], stdin_hex=data.hex(), stdout_hex=expected.hex()))
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
