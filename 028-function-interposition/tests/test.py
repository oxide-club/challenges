#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compila o cliente de teste, sem substituir a aplicação exigida do participante."""
import argparse, json, os, pathlib, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(argv, **kw):
    return subprocess.run(argv, text=True, capture_output=True, timeout=15, **kw)


def check(directory):
    directory = pathlib.Path(directory).resolve()
    with tempfile.TemporaryDirectory(prefix="ox-interpose-") as t:
        app = pathlib.Path(t) / "client"
        p = run(
            [
                "cc",
                "-O0",
                "-fno-lto",
                "-pthread",
                "-rdynamic",
                str(ROOT / "tests/client.c"),
                "-I" + str(ROOT / "materials"),
                "-L" + str(directory),
                "-Wl,--enable-new-dtags",
                "-Wl,-rpath," + str(directory),
                "-lcalc",
                "-o",
                str(app),
            ]
        )
        assert p.returncode == 0, p.stderr
        env = os.environ.copy()
        env.pop("LD_PRELOAD", None)
        baseline = run([str(app), "healthy"], env=env)
        assert baseline.returncode == 0, "baseline: " + baseline.stderr
        cases = json.loads((ROOT / "materials/cases.json").read_text())
        rows = [json.loads(x) for x in baseline.stdout.splitlines()]
        assert len(rows) == 4006, "contagem baseline"
        for row in rows:
            c = cases[row["case"]]
            assert (row["rc"], row["out"], row["after"]) == (
                c["rc"],
                c["out"],
                c["after"],
            ), ("API", row, c)
        for mode in ["healthy", "errno", "fail", "reenter"]:
            env["LD_PRELOAD"] = str(directory / "libtrace.so")
            p = run([str(app), mode], env=env)
            assert p.returncode == 0, (mode, p.returncode, p.stderr[:400])
            assert sorted(p.stdout.splitlines()) == sorted(
                baseline.stdout.splitlines()
            ), ("transparência " + mode)
            records = [json.loads(x) for x in p.stderr.splitlines()]
            if mode == "fail":
                assert not records, "sink com falha"
                continue
            assert len(records) == 4006, ("contagem", mode, len(records))
            assert len({x["call_id"] for x in records}) == 4006, "IDs repetidos"
            assert (
                len({x["thread_id"] for x in records}) == 5
            ), "identificação de threads"
            for x in records:
                assert type(x["call_id"]) is int and x["call_id"] > 0
                assert type(x["thread_id"]) is int and x["thread_id"] > 0
                matches = [
                    c
                    for c in cases
                    if (c["a"], c["b"], c["before"])
                    == (x["a"], x["b"], x["errno_before"])
                ]
                assert len(matches) == 1, "argumentos"
                c = matches[0]
                assert (x["return"], x["errno_after"], x["value"]) == (
                    c["rc"],
                    c["after"],
                    c["out"] if c["rc"] == 0 else None,
                ), "JSON semântico"
        for name in ["app", "direct"]:
            assert (directory / name).is_file(), "aplicação ausente: " + name
        plain = run(
            [str(directory / "app")],
            env={k: v for k, v in env.items() if k != "LD_PRELOAD"},
        )
        direct = run(
            [str(directory / "direct")],
            env={k: v for k, v in env.items() if k != "LD_PRELOAD"},
        )
        assert (
            plain.returncode == direct.returncode == 0
            and plain.stdout == direct.stdout
            and not direct.stderr
        ), "variante direta"
        preloaded = run([str(directory / "direct")], env=env)
        assert (
            preloaded.returncode == 0
            and preloaded.stdout == plain.stdout
            and not preloaded.stderr
        ) or (
            preloaded.returncode == 125 and preloaded.stderr.strip()
        ), "variante direta foi interposta"
        unresolved = pathlib.Path(t) / "unresolved"
        p = run(
            [
                "cc",
                "-rdynamic",
                str(ROOT / "tests/unresolved.c"),
                "-ldl",
                "-o",
                str(unresolved),
            ]
        )
        assert p.returncode == 0, p.stderr
        clean = {k: v for k, v in env.items() if k != "LD_PRELOAD"}
        p = run([str(unresolved), str(directory / "libtrace.so")], env=clean)
        assert p.returncode == 125 and p.stderr.strip(), "resolução sem definição real"
        opaque = pathlib.Path(t) / "libcalc.so"
        p = run(
            ["cc", "-shared", "-fPIC", str(ROOT / "tests/opaque.c"), "-o", str(opaque)]
        )
        assert p.returncode == 0, p.stderr
        clean["LD_LIBRARY_PATH"] = t
        baseline = run([str(app), "healthy"], env=clean)
        assert baseline.returncode == 0 and all(
            json.loads(row)["after"] == 42 for row in baseline.stdout.splitlines()
        ), "controle opaco não carregado"
        clean["LD_PRELOAD"] = str(directory / "libtrace.so")
        for mode in ["healthy", "reenter"]:
            clean["OX_OPAQUE"] = "1"
            clean["OX_EXPECT_CALLS"] = "4007" if mode == "reenter" else "4006"
            traced = run([str(app), mode], env=clean)
            assert baseline.returncode == traced.returncode == 0, (
                "delegação exatamente uma vez",
                mode,
            )
            assert sorted(baseline.stdout.splitlines()) == sorted(
                traced.stdout.splitlines()
            ), "argumentos/retorno opacos"
            assert (
                len([json.loads(x) for x in traced.stderr.splitlines()]) == 4006
            ), "logging aninhado opaco"
        print(
            "PASS API, equivalência, 4000 chamadas, sinks, reentrancy, JSON, chamada direta, resolução e delegação"
        )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    a = p.parse_args()
    try:
        check(a.directory)
    except (AssertionError, subprocess.TimeoutExpired, ValueError) as e:
        p.exit(1, "FAIL " + str(e) + "\n")
