#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Doubles de observações independentes: nenhum resultado aqui é execução WinAPI."""
import copy
import observations as rules
import fixtures
import native_controls

PID, SESSION, DLL = 701, "fixture-control", r"C:\fixture\benign.dll"


def valid():
    def message(phase):
        return dict(
            pid=PID,
            session=SESSION,
            architecture="x64",
            phase=phase,
            ready=True,
            tids=[],
            module=None,
            region=None,
            handles=[],
        )

    initial, active, final = [message(i) for i in range(3)]
    active.update(
        tids=[902, 917], module=DLL, region=dict(base=65536, size=12288, page_size=4096)
    )
    active["handles"] = [dict(id=x, action="create") for x in sorted(rules.HANDLES)]
    next(x for x in active["handles"] if x["id"] == "file-temp")[
        "path"
    ] = r"C:\Temp\oxide.tmp"
    final["handles"] = [dict(id=x, action="close") for x in sorted(rules.HANDLES)]
    observed_active = dict(
        tids=[701, 902, 917, 999],
        modules=[DLL, r"C:\Windows\system32\kernel32.dll"],
        pages=[
            dict(State=0x2000, Protect=0),
            dict(State=0x1000, Protect=4),
            dict(State=0x1000, Protect=2),
        ],
        tempfile_exists=True,
    )
    observed_final = dict(
        tids=[701, 999],
        modules=[r"C:\Windows\system32\kernel32.dll"],
        pages=[dict(State=0x10000) for _ in range(3)],
        tempfile_exists=False,
    )
    return [initial, active, final, observed_active, observed_final]


def check(data):
    initial, active, final, external_active, external_final = data
    rules.initial(initial, PID, SESSION)
    rules.active(active, external_active, PID, SESSION, DLL)
    rules.final(final, external_final, active, PID, SESSION, DLL)


def protocol_controls():
    # O executor double substitui somente WinAPI/processos. O laço e a política
    # de resultado são os mesmos usados por verify() no Windows.
    for collision in (False, True):
        for failure in (None, "ack2", "exit", "missing-dll", "early"):
            events = []

            def execute(mode, defer):
                events.append(mode)
                if mode == "normal":
                    data = valid()
                    if collision:
                        data[4]["tids"].append(902)
                    defer(check, data)
                    events.append("ACK 2")
                    assert failure != "ack2", "falha no ACK 2"
                    events.append("wait")
                    assert failure != "exit", "status final incorreto"
                assert failure != mode, "falha no modo " + mode
                return {"case": mode}

            try:
                result = fixtures.verify(execute)
            except rules.Inconclusive:
                assert collision and failure is None
                assert events == [
                    "normal",
                    "ACK 2",
                    "wait",
                    "missing-dll",
                    "early",
                ], events
            except AssertionError as error:
                assert failure is not None, str(error)
                assert str(error).startswith(("falha no ", "status final")), str(error)
            else:
                assert not collision and failure is None
                assert [r["case"] for r in result] == ["normal", "missing-dll", "early"]
            print("PASS protocolo double:", collision, failure, events)


def main():
    native_controls.main()
    protocol_controls()
    check(valid())
    variants = []
    data = valid()
    data[3]["tids"] += [12345]
    data[4]["tids"] += [54321]
    variants.append(data)
    data = valid()
    data[4]["pages"] = [dict(State=0x10000, Protect=123, Type=456) for _ in range(3)]
    variants.append(data)
    for data in variants:
        check(data)
    data = valid()
    data[4]["tids"].append(902)
    try:
        check(data)
    except rules.Inconclusive:
        print("PASS inconclusivo: consulta final com TID reutilizado")
    else:
        raise AssertionError("colisão de TID não deve aprovar nem reprovar a fixture")
    mutations = {
        "pid-inicial": lambda d: d[0].update(pid=999),
        "sessao-ativa": lambda d: d[1].update(session="other"),
        "pid-final": lambda d: d[2].update(pid=999),
        "sessao-final": lambda d: d[2].update(session="other"),
        "arquitetura": lambda d: d[1].update(architecture="arm64"),
        "sem-prontidao": lambda d: d[1].update(ready=False),
        "sem-fechamentos": lambda d: d[2].update(handles=[]),
        "handle-recriado": lambda d: d[2]["handles"][0].update(action="create"),
        "fechamento-duplicado": lambda d: d[2]["handles"].__setitem__(
            1, copy.deepcopy(d[2]["handles"][0])
        ),
        "worker-publicado-na-fase-final": lambda d: d[2]["tids"].append(902),
        "colisao-nao-oculta-arquivo": lambda d: (
            d[4]["tids"].append(902),
            d[4].update(tempfile_exists=True),
        ),
        "dll-ainda-carregada": lambda d: d[4]["modules"].append(DLL),
        "pagina-nao-liberada": lambda d: d[4]["pages"][1].update(State=0x1000),
        "sem-consulta-final": lambda d: d[4].update(pages=[]),
        "arquivo-nao-removido": lambda d: d[4].update(tempfile_exists=True),
        "arquivo-nunca-existiu": lambda d: d[3].update(tempfile_exists=False),
        "tid-ausente-externo": lambda d: d[3].update(tids=[701, 902]),
        "tid-duplicado": lambda d: d[1].update(tids=[902, 902]),
        "protecao-incorreta": lambda d: d[3]["pages"][2].update(Protect=4),
        "intervalo-incorreto": lambda d: d[1]["region"].update(size=4096),
    }
    for name, mutate in mutations.items():
        data = valid()
        mutate(data)
        try:
            check(data)
        except (AssertionError, KeyError, TypeError, ValueError) as e:
            print("PASS rejeitado:", name, "—", str(e))
        else:
            raise AssertionError("mutante aceito: " + name)
    print(
        "PASS 3 controles conformes, 1 colisão inconclusiva e",
        len(mutations),
        "mutantes; somente doubles, sem WinAPI",
    )


if __name__ == "__main__":
    main()
