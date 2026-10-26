"""SPDX-License-Identifier: MIT. Build isolado C → Rust → C."""

import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(args):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(list(map(str, args)), check=True, timeout=60)


def build(source, work):
    flags = ["-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror"]
    run(
        ["cc", *flags, "-I", source, "-c", source / "rotate.c", "-o", work / "rotate.o"]
    )
    run(["ar", "rcs", work / "librotate.a", work / "rotate.o"])
    run(
        [
            "rustc",
            "--edition=2021",
            "--crate-name",
            "oxide_ffi",
            "--crate-type",
            "staticlib",
            "--crate-type",
            "rlib",
            "--cfg",
            "test_hooks",
            "-C",
            "panic=unwind",
            "-C",
            "opt-level=1",
            source / "rust/lib.rs",
            "--out-dir",
            work,
            "-L",
            work,
            "-l",
            "static=rotate",
        ]
    )
    run(
        [
            "cc",
            *flags,
            "-DOC_TEST_HOOKS",
            "-I",
            source,
            ROOT / "tests/client.c",
            work / "liboxide_ffi.a",
            "-ldl",
            "-lpthread",
            "-lm",
            "-Wl,--wrap=oc_rotate",
            "-o",
            work / "client",
        ]
    )
    run(
        [
            "rustc",
            "--edition=2021",
            ROOT / "tests/helper.rs",
            "-L",
            work,
            "-l",
            "static=rotate",
            "-o",
            work / "helper",
        ]
    )
    run(
        [
            "rustc",
            "--edition=2021",
            ROOT / "tests/layout.rs",
            "--extern",
            f"oxide_ffi={work}/liboxide_ffi.rlib",
            "-L",
            work,
            "-o",
            work / "layout",
        ]
    )


def lsan_run(command, env):
    print("+", " ".join(map(str, command)), "(LSan)", flush=True)
    result = subprocess.run(
        list(map(str, command)), capture_output=True, text=True, timeout=60, env=env
    )
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    return result


def lsan_support(work):
    # Somente a sonda do clube pode classificar indisponibilidade de LSan.
    run(
        [
            "rustc",
            "--edition=2021",
            "--crate-type",
            "staticlib",
            "-C",
            "panic=unwind",
            "-g",
            ROOT / "tests/lsan_probe.rs",
            "-o",
            work / "liblsan_probe.a",
        ]
    )
    run(
        [
            "cc",
            "-O1",
            "-g",
            "-fsanitize=leak",
            ROOT / "tests/lsan_probe.c",
            work / "liblsan_probe.a",
            "-ldl",
            "-lpthread",
            "-lm",
            "-o",
            work / "lsan-probe",
        ]
    )
    raw = subprocess.check_output(
        ["nm", "--defined-only", work / "lsan-probe"], text=True
    )
    symbols = [
        line.split()[-1]
        for line in raw.splitlines()
        if "StaticStrPayload" in line and "take_box" in line
    ]
    assert (
        len(symbols) == 1
    ), "sonda LSan: símbolo exato StaticStrPayload::take_box não identificado"
    # Também permite a grafia demangled do mesmo frame, nunca a crate alloc
    # inteira, oc_transform, oc_create ou um frame genérico de panic.
    demangled = "<std::panicking::panic_handler::StaticStrPayload as core::panic::PanicPayload>::take_box"
    suppression = work / "panic-payload.supp"
    suppression.write_text("leak:^" + symbols[0] + "$\nleak:^" + demangled + "$\n")
    env = dict(
        os.environ,
        LSAN_OPTIONS=f"exitcode=23:fast_unwind_on_malloc=0:suppressions={suppression.resolve()}:print_suppressions=1",
    )
    clean = lsan_run([work / "lsan-probe"], env)
    if "LeakSanitizer has encountered a fatal error" in clean.stderr:
        raise EnvironmentError(
            "LSan indisponível: sonda independente do clube falhou (por exemplo, ptrace)"
        )
    assert clean.returncode == 0, "sonda LSan: supressão do payload não validada"
    leaked = lsan_run([work / "lsan-probe", "leak-context-control"], env)
    assert (
        leaked.returncode == 23 and "37 byte(s)" in leaked.stderr
    ), "sonda LSan: controle de vazamento independente não detectado"
    print(
        "LSan disponível: payload suprimido; vazamento independente de 37 bytes detectado"
    )
    return env


def check_destroy(source, work):
    env = lsan_support(work)
    # Build de distribuição, sem test_hooks: nenhuma supressão necessária.
    release = work / "release"
    release.mkdir(exist_ok=True)
    run(
        [
            "rustc",
            "--edition=2021",
            "--crate-name",
            "oxide_ffi",
            "--crate-type",
            "staticlib",
            "-C",
            "panic=unwind",
            "-C",
            "opt-level=3",
            source / "rust/lib.rs",
            "--out-dir",
            release,
            "-L",
            work,
            "-l",
            "static=rotate",
        ]
    )
    symbols = subprocess.check_output(
        ["nm", "--defined-only", release / "liboxide_ffi.a"],
        text=True,
        stderr=subprocess.DEVNULL,
    )
    assert "oc_test_panic_next" not in symbols
    run(
        [
            "cc",
            "-std=c11",
            "-O1",
            "-g",
            "-fsanitize=leak",
            "-I",
            source,
            ROOT / "tests/destroy.c",
            release / "liboxide_ffi.a",
            "-ldl",
            "-lpthread",
            "-lm",
            "-o",
            work / "destroy",
        ]
    )
    lsan_run(
        [work / "destroy"],
        dict(os.environ, LSAN_OPTIONS="exitcode=23:fast_unwind_on_malloc=0"),
    ).check_returncode()
    run(
        [
            "cc",
            "-std=c11",
            "-O1",
            "-g",
            "-fsanitize=leak",
            "-DOC_TEST_HOOKS",
            "-I",
            source,
            ROOT / "tests/destroy_poison.c",
            work / "liboxide_ffi.a",
            "-ldl",
            "-lpthread",
            "-lm",
            "-o",
            work / "destroy-poison",
        ]
    )
    # Mensagens do candidato nunca transformam falha funcional em status 77.
    lsan_run([work / "destroy-poison"], env).check_returncode()
    print(
        "LSan: destruição normal e após poison conferida; somente payload estático suprimido"
    )


def compile_contract(work):
    calls = [
        "let mut ctx=std::ptr::null_mut(); oxide_ffi::oc_create(0,&mut ctx);",
        "oxide_ffi::oc_destroy(std::ptr::null_mut());",
        "oxide_ffi::oc_transform(std::ptr::null_mut(),std::ptr::null(),0,std::ptr::null_mut(),0);",
    ]
    for index, call in enumerate(calls):
        for valid in (True, False):
            body = ("unsafe { " + call + " }") if valid else call
            source = work / f"client_{index}_{valid}.rs"
            source.write_text("extern crate oxide_ffi; fn main() { " + body + " }")
            r = subprocess.run(
                [
                    "rustc",
                    "--edition=2021",
                    "--emit=metadata",
                    "--error-format=json",
                    str(source),
                    "--extern",
                    f"oxide_ffi={work}/liboxide_ffi.rlib",
                    "-L",
                    str(work),
                    "-o",
                    str(work / "ui.rmeta"),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if valid:
                assert r.returncode == 0, r.stderr
            else:
                import json

                errors = [
                    json.loads(line)
                    for line in r.stderr.splitlines()
                    if line.startswith("{")
                ]
                codes = [e["code"]["code"] for e in errors if e.get("code")]
                assert (
                    r.returncode != 0 and codes and all(c == "E0133" for c in codes)
                ), f'cliente de compilação {source.name} ({["oc_create","oc_destroy","oc_transform"][index]}): chamada sem unsafe deveria falhar somente com E0133; status={r.returncode}, códigos={codes}, stderr={r.stderr}'
    print("Compilação: três pares unsafe/sem unsafe conferidos")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=ROOT / "materials/starter")
    p.add_argument("--prepare", action="store_true")
    p.add_argument("--build-dir", type=Path)
    a = p.parse_args()
    with tempfile.TemporaryDirectory(prefix="oxide-ffi-") as tmp:
        work = a.build_dir or Path(tmp)
        work.mkdir(parents=True, exist_ok=True)
        try:
            run(["python3", ROOT / "materials/generate.py", "--check"])
            build(a.source.resolve(), work)
            run([work / "layout"])
            compile_contract(work)
            symbols = subprocess.check_output(
                ["nm", "--defined-only", work / "client"], text=True
            )
            for name in ("oc_create", "oc_destroy", "oc_transform"):
                assert name in symbols, name
            if not a.prepare:
                run([work / "helper"])
                run([work / "client"])
                check_destroy(a.source.resolve(), work)
            print("Preparação válida" if a.prepare else "Verificações públicas: OK")
            return 0
        except (FileNotFoundError, EnvironmentError) as error:
            print("AMBIENTE INDISPONÍVEL: " + str(error), file=sys.stderr)
            return 77
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            AssertionError,
        ) as error:
            print("FALHOU: " + str(error), file=sys.stderr)
            return 1


if __name__ == "__main__":
    sys.exit(main())
