#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Servidor malformado independente; sucesso não dispensa testar servidor válido."""
import argparse, array, os, pathlib, socket, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def check(candidate):
    candidate = str(pathlib.Path(candidate).resolve())
    size = __import__("json").loads(
        subprocess.check_output([str(ROOT / "build/region-probe")])
    )["size"]
    for case in [
        "missing-fd",
        "extra-fd",
        "wrong-size",
        "wrong-hello",
        "wrong-version",
        "truncated-control",
    ]:
        with tempfile.TemporaryDirectory(prefix="ox-observer-") as d:
            srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            path = d + "/s"
            srv.bind(path)
            srv.listen()
            srv.settimeout(3)
            audit = str(pathlib.Path(d) / "fd-audit.so")
            subprocess.run(
                ["cc", "-shared", "-fPIC", str(ROOT / "tests/fd_audit.c"), "-o", audit],
                check=True,
            )
            env = os.environ.copy()
            env["LD_PRELOAD"] = audit
            read, write = os.pipe()
            token = os.urandom(32)
            p = subprocess.Popen(
                [candidate, path, str(read)],
                pass_fds=[read],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            os.close(read)
            os.write(write, token)
            os.close(write)
            fds = []
            try:
                s, _ = srv.accept()
                s.settimeout(3)
                hello = b""
                while not hello.endswith(b"\n"):
                    assert len(hello) < 256, "HELLO longo"
                    chunk = s.recv(128)
                    assert chunk, "EOF antes de HELLO"
                    hello += chunk
                assert hello == b"HELLO 1 " + token.hex().encode() + b"\n"
                count = (
                    0
                    if case == "missing-fd"
                    else (
                        2
                        if case == "extra-fd"
                        else 32 if case == "truncated-control" else 1
                    )
                )
                for _ in range(count):
                    fd = os.memfd_create("malformed-fixture")
                    os.ftruncate(fd, size)
                    fds.append(fd)
                for fd in fds:
                    subprocess.run(
                        [
                            str(ROOT / "build/region-probe"),
                            str(fd),
                            (
                                "initialize-v2"
                                if case == "wrong-version"
                                else "initialize-v1"
                            ),
                        ],
                        pass_fds=[fd],
                        check=True,
                    )
                    # Mantenha versão, dados e mutex válidos; apenas o tamanho diverge do HELLO.
                    if case == "wrong-size":
                        os.ftruncate(fd, size + 8)
                response = (
                    f"OK 0 HELLO {size}\n".encode()
                    if case != "wrong-hello"
                    else b"OK 1 HELLO 0\n"
                )
                ancillary = (
                    [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", fds))]
                    if fds
                    else []
                )
                s.sendmsg([response[:1]], ancillary)
                s.sendall(response[1:])
                # Mantenha a conexão aberta: EOF não deve causar a rejeição.
                # O observador que aceita HELLO indevidamente envia o primeiro comando.
                try:
                    assert s.recv(256) == b"", (
                        case,
                        "observador aceitou HELLO inválido",
                    )
                except ConnectionResetError:
                    pass
                out, err = p.communicate(timeout=3)
                assert p.returncode == 1, (case, p.returncode, out, err)
                print("PASS observer recusa", case)
            finally:
                if p.poll() is None:
                    p.kill()
                    p.wait()
                for fd in fds:
                    os.close(fd)
                if "s" in locals():
                    s.close()
                srv.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("candidate")
    a = p.parse_args()
    try:
        check(a.candidate)
    except (AssertionError, ValueError, subprocess.TimeoutExpired, OSError) as e:
        p.exit(1, "FAIL " + str(e) + "\n")
