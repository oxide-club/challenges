"""SPDX-License-Identifier: MIT. Fixtures CC0; rotação por rearranjo textual de bits."""

from pathlib import Path
import argparse, json

ROOT = Path(__file__).resolve().parents[1]


def expected():
    return {
        str(key): [
            int((bits := f"{value^key:08b}")[1:] + bits[0], 2) for value in range(256)
        ]
        for key in (0, 90)
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    data = expected()
    text = json.dumps(data, indent=2) + "\n"
    # Blocos fixos de 16 valores mantêm a saída legível e reproduzível,
    # sem exigir um formatador C no ambiente do participante.
    rows = []
    for values in data.values():
        lines = [
            "        " + ", ".join(f"{value:3d}" for value in values[i : i + 16])
            for i in range(0, len(values), 16)
        ]
        rows.append("    {\n" + ",\n".join(lines) + "\n    }")
    header = (
        "/* Dados CC0 1.0; gerados por materials/generate.py. */\n"
        "// clang-format off\n"
        "static const unsigned char expected_bytes[2][256] = {\n"
        + ",\n".join(rows)
        + "\n};\n// clang-format on\n"
    )
    for path, content in [
        (ROOT / "materials/fixtures.json", text),
        (ROOT / "tests/expected.h", header),
    ]:
        if a.check:
            assert path.read_text() == content, path
        else:
            path.write_text(content)
    print("Fixtures: 512 resultados conferidos")


if __name__ == "__main__":
    main()
