"""SPDX-License-Identifier: MIT. Preparação ELF e verificação do núcleo no_std."""

import argparse, os, re, resource, signal, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(argv, **kwargs):
    print("+", " ".join(map(str, argv)), flush=True)
    return subprocess.run(list(map(str, argv)), check=True, timeout=30, **kwargs)


def build(source, work, panic=False):
    output = work / ("panic" if panic else "normal")
    args = [
        "rustc",
        "--edition=2021",
        "--target",
        "x86_64-unknown-linux-gnu",
        "-C",
        "opt-level=3",
        "-C",
        "lto=fat",
        "-C",
        "embed-bitcode=yes",
        "-C",
        "panic=abort",
        "-C",
        "relocation-model=static",
        "-C",
        "linker=cc",
    ]
    for flag in [
        "-nostdlib",
        "-static",
        "-no-pie",
        "-Wl,-e,_start",
        "-Wl,-z,noexecstack",
    ]:
        args += ["-C", "link-arg=" + flag]
    if panic:
        args += ["--cfg", "test_panic"]
    run([*args, source / "main.rs", "-o", output])
    return output


def inspect(binary):
    header = subprocess.check_output(["readelf", "-hW", binary], text=True)
    segments = subprocess.check_output(["readelf", "-lW", binary], text=True)
    dynamic = subprocess.check_output(["readelf", "-dW", binary], text=True)
    symbols = subprocess.check_output(["nm", "-n", binary], text=True)
    assert "ELF64" in header and re.search(r"Type:\s+EXEC", header)
    assert "INTERP" not in segments and "(NEEDED)" not in dynamic
    assert not subprocess.check_output(["nm", "-u", binary]).strip()
    entry = int(re.search(r"Entry point address:\s+(0x[0-9a-f]+)", header)[1], 16)
    start = int(re.search(r"^([0-9a-f]+) T _start$", symbols, re.M)[1], 16)
    assert entry == start
    # Triagem de símbolos sobreviventes a LTO; não substitui a revisão das fontes.
    demangled = subprocess.check_output(["nm", "-C", binary], text=True)
    forbidden = []
    for line in demangled.splitlines():
        parts = line.split(maxsplit=2)
        symbol = parts[-1]
        crate_alloc = re.search(r"(?:^|[\s<(&*])alloc::", symbol)
        allocator = re.fullmatch(
            r"(?:__rustc::)?__(?:rust|rg|rdl)_(?:alloc|dealloc|realloc|alloc_zeroed|alloc_error_handler)",
            symbol,
        )
        if crate_alloc or allocator:
            forbidden.append(line)
    assert not forbidden, ("símbolos de alocação proibida", forbidden)
    return header + segments + dynamic + symbols


class InstrumentationUnavailable(Exception):
    pass


def build_write_limit(work):
    flags = ["-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror"]
    run(["cc", *flags, ROOT / "tests/write_limit.c", "-o", work / "write-limit"])
    run(
        [
            "cc",
            *flags,
            ROOT / "tests/write_limit_probe.c",
            "-o",
            work / "write-limit-probe",
        ]
    )
    run(
        [
            "cc",
            *flags,
            ROOT / "tests/writev_limit_probe.c",
            "-o",
            work / "writev-limit-probe",
        ]
    )


def write_limit_support(work):
    # Sondas só do clube: disponibilidade nunca inferida do stderr do candidato.
    command = [
        str(work / "write-limit"),
        str(work / "write-limit-probe"),
        "single-write",
    ]
    r = subprocess.run(command, capture_output=True, timeout=8)
    print("+", " ".join(command), flush=True)
    print(r.stderr.decode(), end="")
    if r.returncode == 77:
        raise InstrumentationUnavailable(
            "ptrace indisponível na sonda independente de escrita"
        )
    assert (r.returncode, r.stdout) == (0, b"p"), (
        "sonda de escrita única limitada",
        r.returncode,
        r.stdout,
        r.stderr,
    )
    r = subprocess.run(
        [str(work / "write-limit"), str(work / "write-limit-probe")],
        capture_output=True,
        timeout=8,
    )
    print(r.stderr.decode(), end="")
    assert (r.returncode, r.stdout) == (0, b"probe-write\n"), (
        "sonda parcial seguida de sucesso",
        r.returncode,
        r.stdout,
        r.stderr,
    )
    print(
        "Instrumentação validada: escrita única produz 1 byte; laço completa 12 bytes"
    )
    for args, expected in [
        (["single-write"], b"p"),
        ([], b"probe-writev\n"),
        (["edges"], b""),
    ]:
        r = subprocess.run(
            [str(work / "write-limit"), str(work / "writev-limit-probe"), *args],
            capture_output=True,
            timeout=8,
        )
        print(r.stderr.decode(), end="")
        assert (r.returncode, r.stdout) == (0, expected), (
            "sonda writev e restauração do vetor",
            args,
            r.returncode,
            r.stdout,
            r.stderr,
        )
    print(
        "Instrumentação writev validada: escrita única, laço, vetores vazios e erros do kernel"
    )
    return work / "write-limit"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=ROOT / "materials/starter")
    p.add_argument("--prepare", action="store_true")
    p.add_argument("--build-dir", type=Path)
    a = p.parse_args()
    with tempfile.TemporaryDirectory(prefix="oxide-nostd-") as tmp:
        w = a.build_dir or Path(tmp)
        w.mkdir(parents=True, exist_ok=True)
        try:
            run(
                [
                    "cc",
                    "-nostdlib",
                    "-static",
                    "-no-pie",
                    "-Wl,-e,_start",
                    a.source / "start.S",
                    ROOT / "tests/stack.S",
                    "-o",
                    w / "stack",
                ]
            )
            run([w / "stack"])
            normal = build(a.source, w)
            panic = build(a.source, w, True)
            (w / "elf.txt").write_text(inspect(normal))
            (w / "panic-elf.txt").write_text(inspect(panic))
            run(
                [
                    "cc",
                    "-std=c11",
                    "-O1",
                    "-fno-builtin",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    ROOT / "tests/memory.c",
                    a.source / "memory.S",
                    "-o",
                    w / "memory",
                ]
            )
            run([w / "memory"])
            # Copia o mesmo teste público; troca somente a localização do módulo candidato.
            test = (
                (ROOT / "tests/policy.rs")
                .read_text()
                .replace(
                    "../materials/starter/policy.rs",
                    str((a.source / "policy.rs").resolve()),
                )
            )
            (w / "policy-tests.rs").write_text(test)
            run(
                [
                    "rustc",
                    "--edition=2021",
                    "--test",
                    w / "policy-tests.rs",
                    "-o",
                    w / "policy-tests",
                ]
            )
            build_write_limit(w)
            if not a.prepare:
                run([w / "policy-tests"])
                r = subprocess.run([normal], capture_output=True, timeout=2)
                assert (r.returncode, r.stdout) == (0, b"Oxide Club: no_std\n"), (
                    r.returncode,
                    r.stdout,
                )
                r = subprocess.run([panic], capture_output=True, timeout=2)
                assert (r.returncode, r.stdout) == (101, b""), (r.returncode, r.stdout)

                def close_stdout():
                    os.close(1)

                r = subprocess.run(
                    [normal], preexec_fn=close_stdout, stderr=subprocess.PIPE, timeout=2
                )
                assert r.returncode == 74, r.returncode

                def limit_output():
                    resource.setrlimit(resource.RLIMIT_FSIZE, (10, 10))
                    signal.signal(signal.SIGXFSZ, signal.SIG_IGN)

                with tempfile.TemporaryFile() as output:
                    r = subprocess.run(
                        [normal],
                        stdout=output,
                        stderr=subprocess.PIPE,
                        preexec_fn=limit_output,
                        timeout=2,
                    )
                    output.seek(0)
                    data = output.read()
                    assert (r.returncode, data) == (74, b"Oxide Club"), (
                        "RLIMIT_FSIZE=10",
                        r.returncode,
                        data,
                    )
                # Falhas funcionais observáveis sem ptrace não podem virar indisponibilidade.
                limiter = write_limit_support(w)
                r = subprocess.run(
                    [str(limiter), str(normal.resolve())],
                    capture_output=True,
                    timeout=8,
                )
                print(r.stderr.decode(), end="")
                assert (r.returncode, r.stdout) == (0, b"Oxide Club: no_std\n"), (
                    "escritas nativas limitadas a 1 byte",
                    r.returncode,
                    r.stdout,
                    r.stderr,
                )
                observed = re.search(
                    rb"write-limit: stdout_writes=(\d+) limited=\d+ status=0\n\Z",
                    r.stderr,
                )
                assert observed, "instrumento encerrou sem contagem de escritas"
                if int(observed[1]) == 0:
                    raise InstrumentationUnavailable(
                        "saída observada sem write/writev em stdout; mecanismo não coberto pelo tracer"
                    )
            print(
                "Runtime: 19 bytes/status 0; stdout fechado/status 74; panic/status 101"
                if not a.prepare
                else "Núcleo do participante não executado neste modo"
            )
            print("Preparação válida" if a.prepare else "Verificações públicas: OK")
            return 0
        except InstrumentationUnavailable as e:
            print("NÃO EXECUTADO: " + str(e), file=sys.stderr)
            return 77
        except (subprocess.SubprocessError, AssertionError, OSError) as e:
            print("FALHOU: " + str(e), file=sys.stderr)
            return 1


if __name__ == "__main__":
    sys.exit(main())
