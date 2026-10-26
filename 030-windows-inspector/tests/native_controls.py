#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Executa verify/execute reais com doubles de kernel32 e Popen; não chama WinAPI."""
import ctypes
import io
import json
import subprocess
import types
from unittest.mock import patch
import fixtures
import observations


class Function:
    """Aceita também argtypes/restype atribuídos pelo consumidor ctypes."""

    def __init__(self, call):
        self.call = call

    def __call__(self, *args):
        return self.call(*args)


class Process:
    def __init__(self, model, command):
        self.model = model
        self.pid = 701 + len(model.processes)
        self.mode = (
            "early"
            if command[-1] == "early"
            else ("missing-dll" if command[2].endswith("absent.dll") else "normal")
        )
        self.dll = command[2]
        self.returncode = None
        self.killed = False
        self.waits = 0
        self.acks = []
        self.stdin = self
        self.stderr = io.StringIO(
            "LoadLibraryW\n" if self.mode == "missing-dll" else ""
        )
        self.phase = 0

        def message(phase):
            return dict(
                pid=self.pid,
                session=command[1],
                phase=phase,
                ready=True,
                architecture="x64",
                tids=[],
                module=None,
                region=None,
                handles=[],
            )

        initial, active, final = [message(i) for i in range(3)]
        active.update(
            tids=[902, 917],
            module=self.dll,
            region=dict(base=65536, size=12288, page_size=4096),
        )
        active["handles"] = [
            dict(id=name, action="create") for name in sorted(observations.HANDLES)
        ]
        next(h for h in active["handles"] if h["id"] == "file-temp")[
            "path"
        ] = r"C:\double\file.tmp"
        final["handles"] = [
            dict(id=name, action="close") for name in sorted(observations.HANDLES)
        ]
        self.stdout = [
            json.dumps(m) + "\n"
            for m in ([initial, active, final] if self.mode == "normal" else [initial])
        ]
        model.processes.append(self)
        model.current = self

    def reconfigure(self, **kwargs):
        pass

    def flush(self):
        pass

    def write(self, data):
        expected = "ACK " + str(len(self.acks)) + "\n"
        assert data == expected, ("ordem dos ACKs", self.mode, self.acks, data)
        self.acks.append(data)
        self.phase = min(len(self.acks), 2)
        if self.mode != "normal":
            self.returncode = 23 if self.mode == "early" else 1
            if self.model.failure == self.mode:
                self.returncode = 9
        elif data == "ACK 2\n" and self.model.failure != "timeout":
            self.returncode = 3 if self.model.failure == "exit" else 0
        return len(data)

    def wait(self, timeout=None):
        self.waits += 1
        if self.returncode is None:
            # Sem prazo significa que o finally deveria ter terminado o filho.
            assert timeout is not None, "wait sem encerrar filho pendente"
            raise subprocess.TimeoutExpired("alvo double", timeout)
        return self.returncode

    def poll(self):
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9


class Model:
    def __init__(self, collision, failure):
        self.collision, self.failure = collision, failure
        self.processes = []
        self.current = None
        self.error = 0
        self.handles = {}
        self.next_handle = 10
        self.kernel = types.SimpleNamespace()
        for name, call in {
            "CreateToolhelp32Snapshot": self.snapshot,
            "Thread32First": lambda h, r: self.item(h, r, True),
            "Thread32Next": lambda h, r: self.item(h, r, False),
            "Module32FirstW": lambda h, r: self.item(h, r, True),
            "Module32NextW": lambda h, r: self.item(h, r, False),
            "OpenProcess": lambda access, inherit, pid: self.handle(
                ("process", access)
            ),
            "CloseHandle": self.close,
            "VirtualQueryEx": self.query,
        }.items():
            setattr(self.kernel, name, Function(call))

    def handle(self, state):
        self.next_handle += 1
        self.handles[self.next_handle] = state
        return self.next_handle

    def snapshot(self, flags, pid):
        p = self.current
        assert pid == p.pid
        if flags == 4:
            items = [p.pid]
            if p.phase == 1:
                items += [902, 917]
            elif self.collision:
                items += [902]
        else:
            assert flags == 8
            items = [r"C:\double\fixture.exe"]
            if p.phase == 1 or self.failure == "dll":
                items += [p.dll]
        return self.handle(["snapshot", flags, items, 0])

    def item(self, handle, reference, first):
        state = self.handles[handle]
        if first:
            state[3] = 0
        if state[3] == len(state[2]):
            self.error = 18
            return 0
        item = state[2][state[3]]
        state[3] += 1
        reference._obj.pid = self.current.pid
        if state[1] == 4:
            reference._obj.tid = item
        else:
            reference._obj.path = item
        return 1

    def close(self, handle):
        assert handle in self.handles, "fechamento único de handle"
        del self.handles[handle]
        return 1

    def query(self, handle, address, reference, size):
        if self.handles[handle][1] == 0x1000:
            self.error = 5
            return 0
        index = (address - 65536) // 4096
        assert index in range(3)
        page = reference._obj
        page.State, page.Protect = (
            [(0x2000, 0), (0x1000, 4), (0x1000, 2)][index]
            if self.current.phase == 1
            else (0x10000, 0)
        )
        page.RegionSize = 4096
        return size

    def path(self, value):
        assert str(value) == r"C:\double\file.tmp"
        return types.SimpleNamespace(exists=lambda: self.current.phase == 1)


def main():
    # Não substituímos execute, run_modes, defer, observations nem sua ordem.
    # O fluxo nativo faz os ACKs, enumera, espera, decide e libera os recursos.
    for collision in (False, True):
        for failure in (None, "exit", "timeout", "missing-dll", "early", "dll"):
            model = Model(collision, failure)
            result = None
            error = None
            with patch.object(
                fixtures.platform, "system", return_value="Windows"
            ), patch.object(
                ctypes, "WinDLL", return_value=model.kernel, create=True
            ), patch.object(
                ctypes, "get_last_error", side_effect=lambda: model.error, create=True
            ), patch.object(
                fixtures.subprocess,
                "Popen",
                side_effect=lambda cmd, **kw: Process(model, cmd),
            ), patch.object(
                fixtures, "pathlib", types.SimpleNamespace(Path=model.path)
            ):
                try:
                    result = fixtures.verify()
                except (
                    observations.Inconclusive,
                    AssertionError,
                    subprocess.TimeoutExpired,
                ) as caught:
                    error = caught
            expected = (
                subprocess.TimeoutExpired
                if failure == "timeout"
                else (
                    AssertionError
                    if failure
                    else (observations.Inconclusive if collision else None)
                )
            )
            assert type(error) is expected if expected else error is None, (
                collision,
                failure,
                repr(error),
            )
            assert model.processes, "execute nativo não iniciou o alvo"
            for process in model.processes:
                assert process.returncode is not None, ("filho pendente", failure)
                assert process.waits > 0, ("filho sem wait", failure)
            assert not model.handles, ("handles pendentes", model.handles)
            normal = model.processes[0]
            if failure == "dll":
                assert normal.killed and normal.acks == [
                    "ACK 0\n",
                    "ACK 1\n",
                ], "limpeza após falha de observação"
            else:
                assert normal.acks == [
                    "ACK 0\n",
                    "ACK 1\n",
                    "ACK 2\n",
                ], "colisão interrompeu ACK 2"
            if failure == "timeout":
                assert normal.killed, "timeout sem kill"
            expected_modes = (
                ["normal"]
                if failure in ("exit", "timeout", "dll")
                else (
                    ["normal", "missing-dll"]
                    if failure == "missing-dll"
                    else ["normal", "missing-dll", "early"]
                )
            )
            assert [
                p.mode for p in model.processes
            ] == expected_modes, "modo não executado"
            if expected is None:
                assert [row["case"] for row in result] == expected_modes
            print("PASS execute nativo com doubles:", collision, failure)
    print(
        "PASS 12 cenários do fluxo nativo; nenhuma chamada WinAPI ou processo Windows executado"
    )


if __name__ == "__main__":
    main()
