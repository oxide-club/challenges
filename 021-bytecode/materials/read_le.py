def u16(data, offset):
    if offset + 2 > len(data): raise ValueError("truncado")
    return int.from_bytes(data[offset:offset+2], "little")
def i32(data, offset):
    if offset + 4 > len(data): raise ValueError("truncado")
    return int.from_bytes(data[offset:offset+4], "little", signed=True)
