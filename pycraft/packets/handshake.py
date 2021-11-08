import pycraft.utils.formats as formats

def parse_handshake(client, data):
    proto, next_bit = formats.varint_from_data(data)
    address, next_bit = formats.string_from_data(data, current=next_bit)
    port = int.from_bytes(data[next_bit:next_bit+2], "big")
    next_state, next_bit = formats.varint_from_data(data, current=next_bit+2)
    return proto, address, port, next_state