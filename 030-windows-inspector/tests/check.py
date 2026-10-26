#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import argparse
import json
import pathlib
import platform
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
# A integração também executa este arquivo por runpy, sem inserir tests no PATH de módulos.
sys.path.insert(0, str(ROOT / "tests"))
from observations import Inconclusive

HANDLES = {"event-stop", "event-spare", "file-temp"}
ERRORS = {
    "permission-denied",
    "target-exited",
    "incompatible-environment",
    "snapshot-failed",
    "dll-missing",
    "protocol-failed",
}
ORIGINS = dict(
    thread="external",
    module="external",
    memory="external",
    handle="cooperative",
    error="inspector",
)


def positive(value, label):
    assert type(value) is int and value > 0, label


def load(path):
    rows = [
        json.loads(line)
        for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows, "relatório vazio"
    return rows


def validate(rows):
    seen = set()
    sessions = set()
    tids = set()
    for row in rows:
        assert isinstance(row, dict), "registro deve ser objeto"
        assert {
            "session",
            "architecture",
            "phase",
            "category",
            "origin",
            "id",
            "attributes",
        } <= row.keys(), "campos obrigatórios"
        assert isinstance(row["session"], str) and re.fullmatch(
            r"[a-z0-9-]{1,64}", row["session"]
        ), "sessão"
        sessions.add(row["session"])
        assert row["architecture"] == "x64", "arquitetura"
        assert type(row["phase"]) is int and row["phase"] in (0, 1, 2), "fase"
        category = row["category"]
        assert category in ORIGINS, "categoria desconhecida"
        assert row["origin"] == ORIGINS[category], "origem"
        assert isinstance(row["id"], str) and row["id"], "identificador"
        key = row["phase"], category, row["id"]
        assert key not in seen, "registro duplicado"
        seen.add(key)
        attrs = row["attributes"]
        assert isinstance(attrs, dict), "atributos"
        if category == "thread":
            positive(attrs["tid"], "TID positivo")
            key = row["phase"], attrs["tid"]
            assert key not in tids, "TID duplicado na fase"
            tids.add(key)
        elif category == "module":
            assert (
                isinstance(attrs["path"], str)
                and pathlib.PureWindowsPath(attrs["path"]).is_absolute()
            ), "caminho absoluto do módulo"
        elif category == "handle":
            assert row["id"] in HANDLES, "handle selecionado"
            assert row["phase"] in (1, 2), "handle antes da criação"
            assert attrs["action"] == (
                "create" if row["phase"] == 1 else "close"
            ), "histórico de criação/fechamento"
        elif category == "memory":
            assert type(attrs["State"]) is int and attrs["State"] in (
                0x1000,
                0x2000,
                0x10000,
            ), "estado de memória"
            fields = (
                ("Protect", "Type")
                if attrs["State"] == 0x1000
                else (("Type",) if attrs["State"] == 0x2000 else ())
            )
            for field in fields:
                assert type(attrs[field]) is int and attrs[field] >= 0, (
                    "atributo de memória " + field
                )
            positive(attrs["BaseAddress"], "endereço observado")
            positive(attrs["RegionSize"], "tamanho observado")
        else:
            assert attrs["kind"] in ERRORS, "classe de erro"
            api, error = attrs["api"], attrs["error"]
            if api is None:
                assert error is None, "sem API não há GetLastError"
            else:
                assert isinstance(api, str) and api, "nome da API"
                positive(error, "GetLastError positivo")
            if attrs["kind"] in {"permission-denied", "snapshot-failed", "dll-missing"}:
                assert (
                    api is not None
                ), "erro de API deve identificar API e GetLastError"
            if attrs["kind"] == "permission-denied":
                assert error == 5, "ERROR_ACCESS_DENIED"
    assert len(sessions) == 1, "sessão única"


def report(paths):
    assert (
        isinstance(paths, (list, tuple)) and len(paths) == 3
    ), "forneça três relatórios, fases 0, 1 e 2"
    rows = []
    for phase, path in enumerate(paths):
        group = load(path)
        assert all(
            r.get("phase") == phase for r in group
        ), "um arquivo por fase, na ordem 0/1/2"
        rows.extend(group)
    validate(rows)
    for phase in (1, 2):
        assert {
            r["id"] for r in rows if r["phase"] == phase and r["category"] == "handle"
        } == HANDLES, "três handles com criação e fechamento"
    active = [r for r in rows if r["phase"] == 1]
    assert {"worker-0", "worker-1"} <= {
        r["id"] for r in active if r["category"] == "thread"
    }, "workers"
    assert any(
        r["category"] == "module" and r["id"] == "benign-dll" for r in active
    ), "DLL"
    memory = {r["id"]: r["attributes"] for r in active if r["category"] == "memory"}
    assert {"page-0", "page-1", "page-2"} <= memory.keys(), "três páginas didáticas"
    assert memory["page-0"]["State"] == 0x2000, "MEM_RESERVE"
    assert (memory["page-1"]["State"], memory["page-1"]["Protect"]) == (0x1000, 4), "RW"
    assert (memory["page-2"]["State"], memory["page-2"]["Protect"]) == (0x1000, 2), "RO"
    worker_tids = {
        r["attributes"]["tid"]
        for r in active
        if r["category"] == "thread" and r["id"] in {"worker-0", "worker-1"}
    }
    dll_paths = {
        str(pathlib.PureWindowsPath(r["attributes"]["path"])).casefold()
        for r in active
        if r["category"] == "module" and r["id"] == "benign-dll"
    }
    regions = [
        (
            memory[name]["BaseAddress"],
            memory[name]["BaseAddress"] + memory[name]["RegionSize"],
        )
        for name in ("page-0", "page-1", "page-2")
    ]
    reused = set()
    for row in (r for r in rows if r["phase"] == 2):
        attrs = row["attributes"]
        if row["category"] == "thread":
            assert row["id"] not in {
                "worker-0",
                "worker-1",
            }, "worker presente após encerramento"
            if attrs["tid"] in worker_tids:
                reused.add(attrs["tid"])
        elif row["category"] == "module":
            path = str(pathlib.PureWindowsPath(attrs["path"])).casefold()
            assert (
                row["id"] != "benign-dll" and path not in dll_paths
            ), "DLL presente após descarregamento"
        elif row["category"] == "memory":
            start, end = (
                attrs["BaseAddress"],
                attrs["BaseAddress"] + attrs["RegionSize"],
            )
            overlaps = any(start < last and first < end for first, last in regions)
            if overlaps or row["id"] in {"page-0", "page-1", "page-2"}:
                assert (
                    attrs["State"] == 0x10000
                ), "região didática não está MEM_FREE na fase final"
    # Só classifique a ambiguidade depois das verificações de formato e coerência.
    if reused:
        raise Inconclusive(
            "TID didático reaparece com outro identificador; sem identidade adicional, não distingue worker de thread nova"
        )
    print(
        "PASS estrutura dos três relatórios; procedência WinAPI exige execução nativa"
    )


def error_report(path):
    rows = load(path)
    validate(rows)
    assert all(
        r["category"] == "error" for r in rows
    ), "log de erros contém outra categoria"
    print("PASS estrutura do log de erros; não comprova falha WinAPI real")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--report", nargs=3, metavar=("FASE0", "FASE1", "FASE2"))
    parser.add_argument("--error-report")
    args = parser.parse_args()
    try:
        if args.report:
            report(args.report)
        elif args.error_report:
            error_report(args.error_report)
        elif args.prepare:
            for name in [
                "fixture.cpp",
                "benign.cpp",
                "build.ps1",
                "report-template.json",
                "errors.md",
            ]:
                assert (ROOT / "materials" / name).is_file(), name
            json.loads((ROOT / "materials/report-template.json").read_text())
            for name in ("report_controls.py", "fixture_controls.py"):
                subprocess.run(
                    [sys.executable, str(ROOT / "tests" / name)], check=True, timeout=30
                )
            print(
                "PASS controles documentais e doubles; nenhuma chamada WinAPI executada",
                flush=True,
            )
            if platform.system() != "Windows":
                print(
                    "NOT_RUN: build e execução exigem Windows x64; validação nativa pendente"
                )
                return 77
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "materials/build.ps1"),
                ],
                check=True,
                timeout=120,
            )
        else:
            parser.error(
                "use --prepare, --report FASE0 FASE1 FASE2 ou --error-report arquivo"
            )
        return 0
    except Inconclusive as error:
        print("INCONCLUSIVO: " + str(error), file=sys.stderr)
        return 77
    except (
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
        OSError,
        subprocess.SubprocessError,
    ) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
