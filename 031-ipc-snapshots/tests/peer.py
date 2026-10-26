#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Observador adversarial de teste, não é implementação do participante."""
import array, json, os, pathlib, socket, subprocess, sys, time, stat, hashlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CASE = os.environ["OX_CASE"]
MAX = (1 << 64) - 1
path, pipe = sys.argv[1:]
token = b""
assert (
    pathlib.Path(path)
    .resolve()
    .is_relative_to(pathlib.Path(os.environ["TMPDIR"]).resolve())
), "socket fora de TMPDIR"
assert stat.S_IMODE(os.stat(path).st_mode) == 0o600, "socket deve ter modo 0600"
assert (
    stat.S_IMODE(os.stat(pathlib.Path(path).parent).st_mode) == 0o700
), "diretório deve ter modo 0700"
while len(token) < 32:
    b = os.read(int(pipe), 32 - len(token))
    assert b, "token incompleto"
    token += b
os.close(int(pipe))
for pid in [os.getpid(), os.getppid()]:
    for field in ["cmdline", "environ"]:
        raw = pathlib.Path(f"/proc/{pid}/{field}").read_bytes()
        assert token not in raw and token.hex().encode() not in raw, (
            "token exposto em " + field
        )
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(3)
s.connect(path)


def line():
    b = b""
    while not b.endswith(b"\n"):
        x = s.recv(1)
        if not x:
            return b
        b += x
    assert len(b) <= 256
    return b.decode().strip()


def ask(command):
    s.sendall(command.encode() + b"\n")
    return line()


if CASE == "bad-token":
    wrong = bytes([token[0] ^ 1]) + token[1:]
    assert ask("HELLO 1 " + wrong.hex()) == "ERR 0 AUTH"
    assert s.recv(1) == b""
    s.close()
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(3)
    s.connect(path)
hello = ("HELLO 1 " + token.hex() + "\n").encode()
# Fragments não podem virar mensagens independentes.
s.sendall(hello[:8])
time.sleep(0.02)
s.sendall(hello[8:])
data, anc, flags, _ = s.recvmsg(256, socket.CMSG_SPACE(4 * 4))
fds = []
for level, kind, payload in anc:
    if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
        a = array.array("i")
        a.frombytes(payload[: len(payload) // a.itemsize * a.itemsize])
        fds.extend(a)
try:
    assert not flags & (socket.MSG_CTRUNC | socket.MSG_TRUNC), "ancillary truncado"
    assert len(fds) == 1, ("quantidade SCM_RIGHTS", len(fds))
    deadline = time.monotonic() + 2
    while not data.endswith(b"\n"):
        assert len(data) < 256, "HELLO longo"
        left = deadline - time.monotonic()
        assert left > 0, "prazo HELLO"
        s.settimeout(left)
        chunk = s.recv(256 - len(data))
        assert chunk, "EOF em HELLO parcial"
        data += chunk
    s.settimeout(3)
    assert data.startswith(b"OK 0 HELLO ") and data.count(b"\n") == 1
    fd = fds[0]
    size = int(data.split()[3])
    assert os.fstat(fd).st_size == size
    probe = ROOT / "build/region-probe"

    def region(mode="read"):
        p = subprocess.run(
            [str(probe), str(fd), mode],
            pass_fds=[fd],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert p.returncode == 0, (mode, p.stderr)
        return tuple(map(int, p.stdout.split())) if mode == "read" else None

    version, g, c, x = region()
    assert version == 1 and c ^ MAX == x
    if CASE in ["normal", "bad-token"]:
        assert ask("SNAPSHOT 1") == f"OK 1 STATE 0 0 {MAX}"
        assert ask("SET_COUNTER 2 7") == f"OK 2 STATE 1 7 {MAX^7}"
        assert ask("SET_COUNTER 3 7") == f"OK 3 STATE 2 7 {MAX^7}"
        assert ask("BOGUS 4") == "ERR 4 COMMAND"
        assert ask("SET_COUNTER 5 1000001") == "ERR 5 VALUE"
        assert ask("SNAPSHOT 6") == f"OK 6 STATE 2 7 {MAX^7}"
        assert ask("STOP 7") == "OK 7 STOP"
    elif CASE == "worker":
        last = 0
        for seq in range(1, 1001):
            p = ask(f"SNAPSHOT {seq}").split()
            assert p[:3] == ["OK", str(seq), "STATE"]
            g, c, x = map(int, p[3:])
            assert g >= last and 0 <= c <= 1000000 and c ^ MAX == x
            _, later, lc, lx = region()
            assert later >= g and lc ^ MAX == lx
            if later == g:
                assert (lc, lx) == (c, x)
            last = g
        assert ask("STOP 1001") == "OK 1001 STOP"
    elif CASE == "seq-max-stop":
        assert ask(f"STOP {MAX}") == f"OK {MAX} STOP"
    elif CASE == "seq-max-state":
        before = region()
        assert ask(f"SNAPSHOT {MAX}") == f"ERR {MAX} STATE"
        assert region() == before
    elif CASE == "repeat":
        assert ask("SNAPSHOT 1").startswith("OK 1 STATE")
        assert ask("SET_COUNTER 1 7") == "ERR 1 SEQ"
    elif CASE == "long":
        s.sendall(b"X" * 254 + b" 1\n")
        assert line() == "ERR 0 FRAME"
    elif CASE == "boundary":
        # Exatamente 256 bytes inclusive LF: opcode desconhecido, não FRAME.
        assert ask("X" * 253 + " 1") == "ERR 1 COMMAND"
        assert ask("STOP 2") == "OK 2 STOP"
    elif CASE == "extra":
        assert ask("SNAPSHOT 1 extra") == "ERR 1 FRAME"
    elif CASE == "max-generation":
        region("generation-max")
        before = region()
        assert ask("SET_COUNTER 1 7") == "ERR 1 STATE"
        assert region() == before
    elif CASE == "owner-death":
        region("owner-death")
        assert ask("SNAPSHOT 1") == "ERR 1 STATE"
    elif CASE == "disconnect":
        s.close()
    elif CASE == "timeout":
        s.sendall(b"SNAPSHOT ")
        t = time.monotonic()
        assert line() == "ERR 0 TIMEOUT"
        assert 1.8 <= time.monotonic() - t < 2.8, "deadline deve ser dois segundos"
    elif CASE == "lock-timeout":
        h = subprocess.Popen(
            [str(probe), str(fd), "hold"],
            pass_fds=[fd],
            stdout=subprocess.PIPE,
            text=True,
        )
        assert h.stdout.readline() == "LOCKED\n"
        t = time.monotonic()
        assert ask("SNAPSHOT 1") == "ERR 1 TIMEOUT"
        assert 1.8 <= time.monotonic() - t < 2.8, "deadline deve ser dois segundos"
        h.wait(timeout=5)
    else:
        raise AssertionError(CASE)
    if CASE in [
        "seq-max-state",
        "repeat",
        "long",
        "extra",
        "max-generation",
        "owner-death",
        "timeout",
        "lock-timeout",
    ]:
        try:
            assert s.recv(1) == b"", "erro fatal deve fechar conexão e invalidar sessão"
        except ConnectionResetError:
            pass  # fechamento com bytes ainda não consumidos
finally:
    for fd in fds:
        os.close(fd)
    s.close()

pathlib.Path(os.environ["OX_WITNESS"]).write_text(
    json.dumps(
        {
            "case": CASE,
            "nonce": os.environ["OX_WITNESS_NONCE"],
            "token_digest": hashlib.sha256(token).hexdigest(),
        }
    )
)
