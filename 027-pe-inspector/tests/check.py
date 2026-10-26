# SPDX-License-Identifier: MIT
import sys

sys.dont_write_bytecode = True
import argparse, copy, importlib.util, json, pathlib, re, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "fixtures", ROOT / "materials/generate.py"
)
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
CASES = json.loads((ROOT / "tests/cases.json").read_text())
HEX = re.compile(r"0x(?:0|[1-9a-f][0-9a-f]*)\Z")


def validate(obj):
    assert set(obj) == {
        "schema_version",
        "machine",
        "image_base",
        "entry_rva",
        "size_of_headers",
        "data_directories",
        "sections",
        "query",
    }
    assert type(obj["schema_version"]) is int and obj["schema_version"] == 1
    assert obj["machine"] == "0x8664"
    for key in ["image_base", "entry_rva"]:
        assert isinstance(obj[key], str) and HEX.fullmatch(obj[key]), key
    assert type(obj["size_of_headers"]) is int and obj["size_of_headers"] >= 0
    assert isinstance(obj["sections"], list) and 1 <= len(obj["sections"]) <= 96
    for s in obj["sections"]:
        assert set(s) == {"name_hex", "rva", "virtual_size", "raw_offset", "raw_size"}
        assert re.fullmatch("[0-9a-f]{16}", s["name_hex"])
        for k in ["rva", "raw_offset"]:
            assert isinstance(s[k], str) and HEX.fullmatch(s[k])
        for k in ["virtual_size", "raw_size"]:
            assert type(s[k]) is int and 0 <= s[k] <= 0xFFFFFFFF
    assert (
        isinstance(obj["data_directories"], list) and len(obj["data_directories"]) <= 16
    )
    for d in obj["data_directories"]:
        assert (
            set(d) == {"address", "size"}
            and HEX.fullmatch(d["address"])
            and type(d["size"]) is int
            and 0 <= d["size"] <= 0xFFFFFFFF
        )
    q = obj["query"]
    if q is not None:
        assert set(q) == {"rva", "size", "kind", "section_index", "file_offset"}
        assert (
            HEX.fullmatch(q["rva"])
            and type(q["size"]) is int
            and 1 <= q["size"] <= 4096
        )
        assert q["kind"] in [
            "headers",
            "section_raw",
            "zero_fill",
            "cross_region",
            "unmapped",
        ]
        assert (
            q["section_index"] is None
            or type(q["section_index"]) is int
            and 0 <= q["section_index"] < len(obj["sections"])
        )
        assert q["file_offset"] is None or HEX.fullmatch(q["file_offset"])


def prepare():
    with tempfile.TemporaryDirectory(prefix="pe-fixtures-") as d:
        manifest = fixtures.generate(pathlib.Path(d))
        assert manifest == json.loads(
            (ROOT / "materials/fixture-manifest.json").read_text()
        ), "hash/tamanho de fixture divergente"
        # Independente do packer: bytes literais e offsets definidos na tabela PE32+.
        b = (pathlib.Path(d) / "base.bin").read_bytes()
        for field in json.loads((ROOT / "materials/offsets.json").read_text())[
            "fields"
        ]:
            raw = b[field["offset"] : field["offset"] + field["width"]]
            assert (
                raw.hex() == field["hex"]
                if "hex" in field
                else int.from_bytes(raw, "little") == field["value"]
            ), field["name"]
        assert b[:2] == bytes.fromhex("4d5a") and b[128:134] == bytes.fromhex(
            "504500006486"
        )
        assert b[176:184] == bytes.fromhex("0000004001000000")
        assert b[264:288] == bytes.fromhex(
            "2e7465787400000000030000001000000002000000020000"
        )
        small = (pathlib.Path(d) / "optional-small.bin").read_bytes()
        declared = int.from_bytes(small[148:150], "little")
        table = 128 + 24 + declared
        raw_size = int.from_bytes(small[table + 16 : table + 20], "little")
        raw_offset = int.from_bytes(small[table + 20 : table + 24], "little")
        assert (len(small), declared, table, raw_offset, raw_size) == (
            1024,
            111,
            263,
            131072,
            131072,
        ), "derivação de optional-small"
        assert table + 40 <= len(small) and raw_offset + raw_size > len(
            small
        ), "truncated_raw precisa de campos presentes e intervalo além do arquivo"
        for c in CASES:
            if c["status"] == 0:
                validate(c["expected"])
            else:
                allowed = (
                    c["expected"]
                    if isinstance(c["expected"], list)
                    else [c["expected"]]
                )
                assert allowed and all(isinstance(code, str) for code in allowed), c[
                    "id"
                ]
            assert c["fixture"] in manifest or c["fixture"] in [
                "missing",
                "too-large",
                "max-size",
            ]
        good = CASES[0]["expected"]
        for key, value in [
            ("machine", "0X8664"),
            ("image_base", "0x0140000000"),
            ("schema_version", True),
            ("sections", []),
            ("query", {}),
        ]:
            bad = copy.deepcopy(good)
            bad[key] = value
            try:
                validate(bad)
            except (AssertionError, TypeError, KeyError):
                pass
            else:
                raise AssertionError("validador aceitou controle " + key)
    print("OK preparação: fixtures, JSON e cinco controles negativos")


def run(program):
    failures = []
    with tempfile.TemporaryDirectory(prefix="pe-cases-") as d:
        d = pathlib.Path(d)
        fixtures.generate(d)
        with (d / "too-large.bin").open("wb") as f:
            f.write((d / "base.bin").read_bytes())
            f.truncate(64 * 1024 * 1024 + 1)
        with (d / "max-size.bin").open("wb") as f:
            f.write((d / "base.bin").read_bytes())
            f.truncate(64 * 1024 * 1024)
        for c in CASES:
            try:
                r = subprocess.run(
                    [str(program), str(d / (c["fixture"] + ".bin"))] + c["args"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                assert (
                    r.returncode == c["status"]
                ), f'status {r.returncode}, esperado {c["status"]}; {r.stderr[:150]}'
                if r.returncode == 0:
                    obj = json.loads(r.stdout)
                    validate(obj)
                    assert obj == c["expected"], f"JSON divergente: {obj}"
                    assert not r.stderr
                else:
                    assert not r.stdout, "inventário parcial"
                    obj = json.loads(r.stderr)
                    allowed = (
                        c["expected"]
                        if isinstance(c["expected"], list)
                        else [c["expected"]]
                    )
                    assert (
                        obj["code"] in allowed
                    ), f"diagnóstico {obj}; códigos aceitos: {allowed}"
                    assert (
                        isinstance(obj["field"], str)
                        and obj["field"]
                        and HEX.fullmatch(obj["offset"])
                    )
            except (
                AssertionError,
                ValueError,
                TypeError,
                KeyError,
                subprocess.TimeoutExpired,
            ) as e:
                failures.append((c["id"], str(e)))
    for id, msg in failures:
        print("FAIL", id, msg)
    print(f"{len(CASES)-len(failures)}/{len(CASES)} casos aprovados")
    return not failures


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("program", nargs="?", type=pathlib.Path)
    p.add_argument("--prepare", action="store_true")
    a = p.parse_args()
    if a.prepare:
        prepare()
    elif a.program:
        raise SystemExit(0 if run(a.program.resolve()) else 1)
    else:
        p.error("informe programa ou --prepare")
