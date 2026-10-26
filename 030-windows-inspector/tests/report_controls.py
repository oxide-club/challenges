#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Controles sintéticos do consumidor; não são evidência de WinAPI."""
import contextlib
import copy
import io
import json
import pathlib
import subprocess
import sys
import tempfile
from check import report, error_report, ERRORS, Inconclusive


def valid():
    rows = []

    def add(phase, category, ident, attrs):
        rows.append(
            dict(
                session="synthetic-control",
                architecture="x64",
                phase=phase,
                category=category,
                origin="cooperative" if category == "handle" else "external",
                id=ident,
                attributes=attrs,
            )
        )

    add(0, "thread", "main", {"tid": 100})
    add(2, "thread", "main", {"tid": 100})
    for i in range(2):
        add(1, "thread", "worker-" + str(i), {"tid": 101 + i})
    add(1, "module", "benign-dll", {"path": r"C:\fixture\benign.dll"})
    for i, (state, protect) in enumerate([(0x2000, 0), (0x1000, 4), (0x1000, 2)]):
        add(
            1,
            "memory",
            "page-" + str(i),
            dict(
                State=state,
                Protect=protect,
                Type=0x20000,
                BaseAddress=65536 + i * 4096,
                RegionSize=4096,
            ),
        )
    for ident in ["event-stop", "event-spare", "file-temp"]:
        add(1, "handle", ident, {"action": "create"})
        add(2, "handle", ident, {"action": "close"})
    return rows


def main():
    with tempfile.TemporaryDirectory() as directory:
        paths = [pathlib.Path(directory) / f"phase-{i}.jsonl" for i in range(3)]

        def check(data):
            for phase, path in enumerate(paths):
                path.write_text(
                    "".join(json.dumps(r) + "\n" for r in data if r["phase"] == phase)
                )
            with contextlib.redirect_stdout(io.StringIO()):
                report(paths)

        check(valid())
        variant = valid()
        # TIDs e sessão variam; ordem dos registros dentro da fase não é normativa.
        for row in variant:
            row["session"] = "another-session"
            if row["category"] == "thread":
                row["attributes"]["tid"] += 5000
        check(list(reversed(variant)))
        variant = valid()
        for row in variant:
            if row["id"] == "page-0":
                row["attributes"].pop("Protect")
        variant.append(
            dict(
                session="synthetic-control",
                architecture="x64",
                phase=2,
                category="memory",
                origin="external",
                id="released-region",
                attributes=dict(State=0x10000, BaseAddress=65536, RegionSize=12288),
            )
        )
        check(variant)
        # TID reutilizado não demonstra continuidade da thread antiga.
        # O mesmo JSON também pode ocultar um worker renomeado: nunca aprovar.
        for ident in ("tp-worker", "other-thread"):
            variant = repeat_final(valid(), "worker-0", ident)
            try:
                check(variant)
            except Inconclusive:
                pass
            else:
                raise AssertionError("colisão de TID deveria ser inconclusiva")
            result = subprocess.run(
                [
                    sys.executable,
                    str(pathlib.Path(__file__).with_name("check.py")),
                    "--report",
                    *map(str, paths),
                ],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 77 and "INCONCLUSIVO" in result.stderr, (
                result.returncode,
                result.stderr,
            )
            print("PASS inconclusivo: TID reutilizado com identificador", ident)
        # A liberação pode aparecer como região livre coalescida; memória alheia continua permitida.
        variant = valid()
        variant.append(
            dict(
                session="synthetic-control",
                architecture="x64",
                phase=2,
                category="memory",
                origin="external",
                id="other-region",
                attributes=dict(
                    State=0x1000,
                    Protect=4,
                    Type=0x20000,
                    BaseAddress=1048576,
                    RegionSize=4096,
                ),
            )
        )
        check(variant)
        mutations = {
            "missing-phase": lambda d: [r for r in d if r["phase"] != 2],
            "false-origin": lambda d: change(d, "file-temp", "origin", "external"),
            "missing-worker": lambda d: [r for r in d if r["id"] != "worker-1"],
            "missing-dll": lambda d: [r for r in d if r["id"] != "benign-dll"],
            "wrong-protection": lambda d: attribute(d, "page-2", "Protect", 4),
            "missing-page": lambda d: [r for r in d if r["id"] != "page-1"],
            "missing-close": lambda d: [
                r for r in d if not (r["category"] == "handle" and r["phase"] == 2)
            ],
            "missing-tid": lambda d: remove_attribute(d, "worker-0", "tid"),
            "bool-tid": lambda d: attribute(d, "worker-0", "tid", True),
            "duplicate-tid": lambda d: attribute(d, "worker-1", "tid", 101),
            "unknown-category": lambda d: change(d, "main", "category", "anything"),
            "recreated-handle": lambda d: recreate(d),
            "missing-architecture": lambda d: remove_field(d, "architecture"),
            "wrong-architecture": lambda d: change(d, "main", "architecture", "arm64"),
            "mixed-session": lambda d: change(d, "worker-0", "session", "other"),
            "duplicate-record": lambda d: d + [copy.deepcopy(d[-1])],
            "final-worker": lambda d: repeat_final(d, "worker-0"),
            "collision-with-live-worker": lambda d: repeat_final(
                repeat_final(d, "worker-0", "other-thread"), "worker-1"
            ),
            "collision-with-live-dll": lambda d: repeat_final(
                repeat_final(d, "worker-0", "other-thread"), "benign-dll"
            ),
            "final-dll": lambda d: repeat_final(d, "benign-dll"),
            "final-dll-renamed": lambda d: repeat_final(
                d, "benign-dll", "other-module"
            ),
            "final-committed-page": lambda d: repeat_final(d, "page-1"),
            "final-committed-page-renamed": lambda d: repeat_final(
                d, "page-1", "other-page"
            ),
            "final-reserved-page": lambda d: repeat_final(d, "page-0"),
        }
        for name, mutate in mutations.items():
            try:
                check(mutate(valid()))
            except (AssertionError, KeyError, TypeError, ValueError) as error:
                print("PASS recusado:", name, "—", str(error))
            else:
                raise AssertionError("controle aceito: " + name)
        errors = []
        for kind in sorted(ERRORS):
            api, error = (None, None)
            if kind == "permission-denied":
                api, error = "VirtualQueryEx", 5
            elif kind == "dll-missing":
                api, error = "LoadLibraryW", 126
            elif kind == "snapshot-failed":
                api, error = "CreateToolhelp32Snapshot", 24
            errors.append(
                dict(
                    session="synthetic-control",
                    architecture="x64",
                    phase=1,
                    category="error",
                    origin="inspector",
                    id=kind,
                    attributes=dict(kind=kind, api=api, error=error),
                )
            )
        path = pathlib.Path(directory) / "errors.jsonl"

        def errors_check(data):
            path.write_text("".join(json.dumps(row) + "\n" for row in data))
            with contextlib.redirect_stdout(io.StringIO()):
                error_report(path)

        errors_check(errors)
        for name, field, value in [
            ("error-origin", "origin", "external"),
            ("error-kind", "kind", "unknown"),
            ("error-code", "error", 0),
        ]:
            bad = copy.deepcopy(errors)
            row = next(r for r in bad if r["attributes"]["kind"] == "permission-denied")
            (row if field == "origin" else row["attributes"])[field] = value
            try:
                errors_check(bad)
            except (AssertionError, KeyError, TypeError, ValueError) as error:
                print("PASS recusado:", name, "—", str(error))
            else:
                raise AssertionError("controle de erro aceito: " + name)
    print(
        "PASS 4 relatórios conformes, 2 colisões inconclusivas, 6 classes de erro e 27 mutantes; nenhuma chamada WinAPI"
    )


def change(data, ident, key, value):
    next(r for r in data if r["id"] == ident)[key] = value
    return data


def attribute(data, ident, key, value):
    next(r for r in data if r["id"] == ident)["attributes"][key] = value
    return data


def remove_attribute(data, ident, key):
    del next(r for r in data if r["id"] == ident)["attributes"][key]
    return data


def remove_field(data, key):
    del data[0][key]
    return data


def recreate(data):
    next(r for r in data if r["category"] == "handle" and r["phase"] == 2)[
        "attributes"
    ]["action"] = "create"
    return data


def repeat_final(data, ident, new_id=None):
    row = copy.deepcopy(next(r for r in data if r["phase"] == 1 and r["id"] == ident))
    row["phase"] = 2
    if new_id is not None:
        row["id"] = new_id
    return data + [row]


if __name__ == "__main__":
    main()
