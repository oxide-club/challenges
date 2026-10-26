#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile pares de clientes contra esta biblioteca. Nunca execute os clientes inválidos."""
import json, pathlib, subprocess, tempfile, sys

root = pathlib.Path(__file__).resolve().parents[1]
name = (
    root.joinpath("Cargo.toml")
    .read_text()
    .split('name = "')[1]
    .split('"')[0]
    .replace("-", "_")
)
subprocess.run(["cargo", "build", "--offline"], cwd=root, check=True)
with tempfile.TemporaryDirectory(prefix="oxide-ui-") as temp:
    for case in json.loads((root / "tests/ui/cases.json").read_text()):
        for kind in ["pass", "fail"]:
            source = root / "tests/ui" / f"{case['id']}.{kind}.rs"
            cmd = [
                "rustc",
                "--edition=2021",
                "--crate-name",
                "client",
                str(source),
                "--extern",
                f"{name}={root}/target/debug/lib{name}.rlib",
                "-L",
                f"dependency={root}/target/debug/deps",
                "--error-format=json",
                "-o",
                f"{temp}/client",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            diagnostics = [
                json.loads(line)
                for line in result.stderr.splitlines()
                if line.startswith("{")
            ]
            errors = [
                d for d in diagnostics if d.get("level") == "error" and d.get("code")
            ]
            codes = {d["code"]["code"] for d in errors}
            ok = (
                result.returncode == 0
                if kind == "pass"
                else result.returncode != 0
                and case["code"] in codes
                and not codes.intersection({"E0432", "E0433", "E0463", "E0425"})
            )
            print(case["id"], kind, "PASS" if ok else "FAIL", sorted(codes))
            if not ok:
                print(result.stderr)
                sys.exit(1)
