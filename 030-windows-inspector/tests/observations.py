# SPDX-License-Identifier: MIT
"""Regras puras sobre mensagens e observações independentes; não chama WinAPI."""
import pathlib

HANDLES = {"event-stop", "event-spare", "file-temp"}


class Inconclusive(Exception):
    """Os atributos observados não distinguem reúso de identidade."""


def integer(value, label):
    assert type(value) is int and value > 0, label


def identity(message, pid, session, phase):
    assert message["pid"] == pid and type(message["pid"]) is int, "PID do filho"
    assert message["session"] == session, "sessão do filho"
    assert message["architecture"] == "x64", "arquitetura do filho"
    assert type(message["phase"]) is int and message["phase"] == phase, "fase"
    assert message["ready"] is True, "prontidão"


def handles(items, action):
    assert (
        len(items) == 3 and {x["id"] for x in items} == HANDLES
    ), "três handles distintos"
    assert all(x["action"] == action for x in items), "ação dos handles"


def initial(message, pid, session):
    identity(message, pid, session, 0)
    assert (
        message["tids"] == [] and message["handles"] == []
    ), "inventário inicial vazio"
    assert (
        message["module"] is None and message["region"] is None
    ), "recursos iniciais ausentes"


def active(message, observation, pid, session, dll):
    identity(message, pid, session, 1)
    handles(message["handles"], "create")
    tids = message["tids"]
    assert len(tids) == 2 and len(set(tids)) == 2, "dois TIDs distintos"
    for tid in tids:
        integer(tid, "TID positivo")
    assert set(tids) <= set(observation["tids"]), "workers observados externamente"
    assert message["module"].casefold() == dll.casefold(), "identidade da DLL publicada"
    assert dll.casefold() in {
        p.casefold() for p in observation["modules"]
    }, "DLL observada"
    region = message["region"]
    for key in ("base", "size", "page_size"):
        integer(region[key], "região " + key)
    assert region["size"] == 3 * region["page_size"], "intervalo de três páginas"
    assert region["base"] % region["page_size"] == 0, "base alinhada"
    pages = observation["pages"]
    assert len(pages) == 3, "três consultas de página"
    assert pages[0]["State"] == 0x2000, "MEM_RESERVE"
    assert (pages[1]["State"], pages[1]["Protect"]) == (0x1000, 4), "RW"
    assert (pages[2]["State"], pages[2]["Protect"]) == (0x1000, 2), "RO"
    temp = next(x for x in message["handles"] if x["id"] == "file-temp")["path"]
    assert (
        isinstance(temp, str) and pathlib.PureWindowsPath(temp).is_absolute()
    ), "caminho temporário absoluto"
    assert observation["tempfile_exists"] is True, "arquivo temporário existente"


def final(message, observation, previous, pid, session, dll):
    identity(message, pid, session, 2)
    handles(message["handles"], "close")
    assert (
        message["tids"] == []
        and message["module"] is None
        and message["region"] is None
    ), "inventário final vazio"
    reused = set(previous["tids"]) & set(observation["tids"])
    assert dll.casefold() not in {
        p.casefold() for p in observation["modules"]
    }, "DLL ainda presente"
    pages = observation["pages"]
    assert len(pages) == 3 and all(
        p["State"] == 0x10000 for p in pages
    ), "MEM_FREE no intervalo liberado"
    # Protect/Type não são definidos para MEM_FREE; não os comparamos.
    assert observation["tempfile_exists"] is False, "arquivo temporário não removido"
    if reused:
        raise Inconclusive(
            "TID didático reaparece na consulta final; sem identidade adicional, não distingue worker de thread nova"
        )
