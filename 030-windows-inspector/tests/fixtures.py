#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verifica o alvo do clube por APIs independentes; requer Windows x64."""
import argparse, ctypes as C, json, pathlib, platform, queue, subprocess, threading, uuid, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
import observations


def run_modes(execute):
    """Adia somente colisões; erros de protocolo e de outros modos prevalecem."""
    collisions = []

    def defer(check, *args):
        try:
            check(*args)
        except observations.Inconclusive as error:
            collisions.append(str(error))

    records = [execute(mode, defer) for mode in ["normal", "missing-dll", "early"]]
    if collisions:
        raise observations.Inconclusive("; ".join(collisions))
    return records


def verify(execute=None):
    if execute is not None:
        return run_modes(execute)

    from ctypes import wintypes as W

    assert (
        platform.system() == "Windows" and C.sizeof(C.c_void_p) == 8
    ), "Windows x64 necessário"
    k = C.WinDLL("kernel32", use_last_error=True)

    class THREAD(C.Structure):
        _fields_ = [
            ("size", W.DWORD),
            ("usage", W.DWORD),
            ("tid", W.DWORD),
            ("pid", W.DWORD),
            ("base", W.LONG),
            ("delta", W.LONG),
            ("flags", W.DWORD),
        ]

    class MODULE(C.Structure):
        _fields_ = [
            ("size", W.DWORD),
            ("id", W.DWORD),
            ("pid", W.DWORD),
            ("global_usage", W.DWORD),
            ("usage", W.DWORD),
            ("base", C.c_void_p),
            ("base_size", W.DWORD),
            ("module", W.HMODULE),
            ("name", W.WCHAR * 256),
            ("path", W.WCHAR * 260),
        ]

    class MEMORY(C.Structure):
        _fields_ = [
            ("BaseAddress", C.c_void_p),
            ("AllocationBase", C.c_void_p),
            ("AllocationProtect", W.DWORD),
            ("PartitionId", W.WORD),
            ("RegionSize", C.c_size_t),
            ("State", W.DWORD),
            ("Protect", W.DWORD),
            ("Type", W.DWORD),
        ]

    k.CreateToolhelp32Snapshot.argtypes = [W.DWORD, W.DWORD]
    k.CreateToolhelp32Snapshot.restype = W.HANDLE
    k.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
    k.OpenProcess.restype = W.HANDLE
    k.CloseHandle.argtypes = [W.HANDLE]
    k.CloseHandle.restype = W.BOOL
    k.VirtualQueryEx.argtypes = [W.HANDLE, C.c_void_p, C.POINTER(MEMORY), C.c_size_t]
    k.VirtualQueryEx.restype = C.c_size_t

    def enumeration(pid, module=False):
        deadline = time.monotonic() + 2
        h = C.c_void_p(-1).value
        for attempt in range(10):
            h = k.CreateToolhelp32Snapshot(8 if module else 4, pid)
            if h != C.c_void_p(-1).value:
                break
            error = C.get_last_error()
            assert error == 24, ("CreateToolhelp32Snapshot", error)
            if time.monotonic() >= deadline:
                break
            time.sleep(0.01)
        assert h != C.c_void_p(-1).value, (
            "CreateToolhelp32Snapshot",
            "tentativas/prazo esgotados",
            C.get_last_error(),
        )
        typ = MODULE if module else THREAD
        item = typ()
        item.size = C.sizeof(item)
        first = k.Module32FirstW if module else k.Thread32First
        next_ = k.Module32NextW if module else k.Thread32Next
        for f in [first, next_]:
            f.argtypes = [W.HANDLE, C.POINTER(typ)]
            f.restype = W.BOOL
        out = []
        try:
            more = first(h, C.byref(item))
            while more:
                if item.pid == pid:
                    out.append(item.path if module else item.tid)
                more = next_(h, C.byref(item))
            assert C.get_last_error() == 18, (
                "Module32NextW/Thread32Next" if out else "Module32FirstW/Thread32First",
                C.get_last_error(),
            )
        finally:
            k.CloseHandle(h)
        return out

    def collect(proc, q):
        for line in proc.stdout:
            q.put(line)
        q.put(None)

    def execute(mode, defer):
        dll = (
            (ROOT / "build/benign.dll").resolve()
            if mode != "missing-dll"
            else (ROOT / "build/absent.dll").resolve()
        )
        session = str(uuid.uuid4())
        command = [str(ROOT / "build/fixture.exe"), session, str(dll)] + (
            ["early"] if mode == "early" else []
        )
        p = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        p.stdin.reconfigure(newline="\n")
        q = queue.Queue()
        threading.Thread(target=collect, args=(p, q), daemon=True).start()
        try:
            initial = json.loads(q.get(timeout=5))
            observations.initial(initial, p.pid, session)
            p.stdin.write("ACK 0\n")
            p.stdin.flush()
            if mode != "normal":
                p.wait(timeout=5)
                stderr = p.stderr.read()
                assert p.returncode == (23 if mode == "early" else 1)
                if mode == "missing-dll":
                    assert "LoadLibraryW" in stderr
                return {"case": mode, "status": p.returncode, "stderr": stderr}
            active = json.loads(q.get(timeout=5))
            assert active["phase"] == 1 and active["architecture"] == "x64"
            tids = enumeration(p.pid)
            modules = enumeration(p.pid, True)
            assert len(active["tids"]) == 2 and set(active["tids"]) <= set(tids)
            assert str(dll).casefold() in {x.casefold() for x in modules}
            assert {x["id"] for x in active["handles"]} == {
                "event-stop",
                "event-spare",
                "file-temp",
            }
            h = k.OpenProcess(0x0400, False, p.pid)
            assert h, ("OpenProcess", C.get_last_error())
            pages = []
            try:
                for i in range(3):
                    m = MEMORY()
                    a = active["region"]["base"] + i * active["region"]["page_size"]
                    assert k.VirtualQueryEx(h, a, C.byref(m), C.sizeof(m)) == C.sizeof(
                        m
                    )
                    pages.append(
                        {
                            "State": m.State,
                            "Protect": m.Protect,
                            "Type": m.Type,
                            "RegionSize": m.RegionSize,
                        }
                    )
            finally:
                k.CloseHandle(h)
            temporary = pathlib.Path(
                next(x for x in active["handles"] if x["id"] == "file-temp")["path"]
            )
            active_observation = {
                "tids": tids,
                "modules": modules,
                "pages": pages,
                "tempfile_exists": temporary.exists(),
            }
            observations.active(active, active_observation, p.pid, session, str(dll))
            limited = k.OpenProcess(0x1000, False, p.pid)
            assert limited
            try:
                m = MEMORY()
                assert (
                    k.VirtualQueryEx(
                        limited, active["region"]["base"], C.byref(m), C.sizeof(m)
                    )
                    == 0
                )
                assert C.get_last_error() == 5
            finally:
                k.CloseHandle(limited)
            p.stdin.write("ACK 1\n")
            p.stdin.flush()
            final = json.loads(q.get(timeout=5))
            assert final["phase"] == 2
            released = []
            h = k.OpenProcess(0x0400, False, p.pid)
            assert h, ("OpenProcess final", C.get_last_error())
            try:
                for i in range(3):
                    m = MEMORY()
                    address = (
                        active["region"]["base"] + i * active["region"]["page_size"]
                    )
                    assert k.VirtualQueryEx(
                        h, address, C.byref(m), C.sizeof(m)
                    ) == C.sizeof(m), ("VirtualQueryEx final", C.get_last_error())
                    released.append({"State": m.State, "RegionSize": m.RegionSize})
            finally:
                k.CloseHandle(h)
            final_observation = {
                "tids": enumeration(p.pid),
                "modules": enumeration(p.pid, True),
                "pages": released,
                "tempfile_exists": temporary.exists(),
            }
            defer(
                observations.final,
                final,
                final_observation,
                active,
                p.pid,
                session,
                str(dll),
            )
            p.stdin.write("ACK 2\n")
            p.stdin.flush()
            p.wait(timeout=5)
            assert p.returncode == 0
            return {
                "case": "normal",
                "initial": initial,
                "active": active,
                "final": final,
                "pages": pages,
                "external_tids": tids,
                "external_modules": modules,
                "active_observation": active_observation,
                "final_observation": final_observation,
            }
        finally:
            if p.poll() is None:
                p.kill()
                p.wait()

    return run_modes(execute)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output")
    a = p.parse_args()
    if platform.system() != "Windows":
        p.exit(77, "NOT_RUN Windows x64 necessário\n")
    try:
        result = verify()
        print("PASS fixtures, fases, TIDs, DLL, memória e três caminhos de erro")
        if a.output:
            pathlib.Path(a.output).write_text(json.dumps(result, indent=2) + "\n")
    except observations.Inconclusive as e:
        p.exit(77, "INCONCLUSIVO: " + str(e) + "\n")
    except (
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
        OSError,
        queue.Empty,
        subprocess.TimeoutExpired,
    ) as e:
        p.exit(1, "FAIL " + str(e) + "\n")
