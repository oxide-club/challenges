# SPDX-License-Identifier: MIT
"""Fixtures sintéticas CC0; revisão 2. Gera bytes, nunca executa imagens."""
import argparse, hashlib, json, pathlib, struct


def base(sections=1, dirs=0, extra=0):
    opt = 112 + dirs * 8 + extra
    table = 0x98 + opt
    headers = max(0x200, (table + sections * 40 + 511) // 512 * 512)
    b = bytearray(headers + 512 * sections)
    b[:2] = b"MZ"
    struct.pack_into("<I", b, 0x3C, 0x80)
    b[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HH", b, 0x84, 0x8664, sections)
    struct.pack_into("<H", b, 0x94, opt)
    struct.pack_into("<H", b, 0x98, 0x20B)
    struct.pack_into("<I", b, 0xA8, 0x1010)
    struct.pack_into("<Q", b, 0xB0, 0x140000000)
    struct.pack_into("<I", b, 0xD4, headers)
    struct.pack_into("<I", b, 0x104, dirs)
    for i in range(dirs):
        struct.pack_into("<II", b, 0x108 + i * 8, 0xF0000000 + i, 17 + i)
    for i in range(sections):
        off = table + i * 40
        b[off : off + 8] = b".text\0\0\0" if i == 0 else b".data\0\0\0"
        struct.pack_into(
            "<IIII",
            b,
            off + 8,
            0x300,
            (0x2000 if sections == 96 else 0x1000) + i * 0x1000,
            512,
            headers + i * 512,
        )
    return b, table


def fixtures():
    b, t = base()
    out = {
        "base": b,
        "overlay": b + b"OVERLAY",
        "dos-short": b[:63],
        "pe-short": b[:0x97],
        "optional-short": b[:0x107],
        "sections-short": b[: t + 39],
        "raw-short": b[:-1],
    }

    def edit(name, off, fmt, value, source=b):
        x = bytearray(source)
        struct.pack_into(fmt, x, off, value)
        out[name] = x

    for name, off, fmt, value in [
        ("bad-mz", 0, "<H", 0),
        ("bad-pe", 0x80, "<I", 0),
        ("machine", 0x84, "<H", 0x14C),
        ("pe32", 0x98, "<H", 0x10B),
        ("count-zero", 0x86, "<H", 0),
        ("count-97", 0x86, "<H", 97),
        ("optional-small", 0x94, "<H", 111),
        ("dirs-17", 0x104, "<I", 17),
        ("dirs-short", 0x104, "<I", 1),
        ("headers-small", 0xD4, "<I", t + 39),
        ("headers-large", 0xD4, "<I", 1025),
        ("raw-in-headers", t + 20, "<I", 511),
        ("rva-in-headers", t + 12, "<I", 511),
        ("rva-overflow", t + 12, "<I", 0xFFFFFF00),
        ("virtual-zero-raw", t + 8, "<I", 0),
        ("padding", t + 8, "<I", 256),
        ("top-boundary", t + 12, "<I", 0xFFFFFD00),
        ("e-lfanew-huge", 0x3C, "<I", 0xFFFFFFFF),
        ("raw-pointer-huge", t + 20, "<I", 0xFFFFFFF0),
    ]:
        edit(name, off, fmt, value)
    x = bytearray(b)
    struct.pack_into("<II", x, t + 8, 0, 0)
    struct.pack_into("<II", x, t + 16, 0, 0xFFFFFFFF)
    out["empty"] = x
    x = bytearray(b)
    struct.pack_into("<II", x, t + 16, 0, 0xFFFFFFFF)
    out["zero-fill-only"] = x
    x, t2 = base(2)
    out["two"] = x
    reversed_table = bytearray(x)
    reversed_table[t2 : t2 + 40], reversed_table[t2 + 40 : t2 + 80] = (
        x[t2 + 40 : t2 + 80],
        x[t2 : t2 + 40],
    )
    out["reverse-table"] = reversed_table
    touching = bytearray(x)
    struct.pack_into("<I", touching, t2 + 40 + 12, 0x1300)
    out["virtual-touch"] = touching
    edit("raw-overlap", t2 + 40 + 20, "<I", 512, x)
    edit("virtual-overlap", t2 + 40 + 12, "<I", 0x1100, x)
    out["directories"], _ = base(dirs=16, extra=8)
    out["count-96"], _ = base(96)
    x = bytearray(b)
    x[t : t + 8] = bytes.fromhex("00ff227f80414243")
    out["binary-name"] = x
    # Isolar contagem e SizeOfHeaders de outras violações de intervalo.
    x, t97 = base(97)
    for i in range(97):
        struct.pack_into("<I", x, t97 + i * 40 + 12, 0x2000 + i * 0x1000)
    out["count-97"] = x
    x = bytearray(b)
    struct.pack_into("<I", x, 0xD4, len(b) + 1)
    struct.pack_into("<IIII", x, t + 8, 0, 0, 0, 0)
    out["headers-large"] = x
    edit("headers-exact", 0xD4, "<I", t + 40)
    edit("optional-declared-truncated", 0x94, "<H", 65535)
    return out


def generate(dest):
    dest.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, data in fixtures().items():
        (dest / (name + ".bin")).write_bytes(data)
        manifest[name] = {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directory", type=pathlib.Path)
    a = p.parse_args()
    generate(a.directory)
