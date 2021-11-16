def varint_from_data(data, current=0):
    value = 0
    for offset in range(0,36,7):
        value |= (data[current] & 0b01111111) << offset
        if (data[current] & 0b10000000) == 0:
            return value, current + 1
        current += 1
    else:
        raise ValueError("VarInt is too big")

def encode_step_int(value):
    byte = value & 0b01111111
    value = value >> 7
    if value != 0:
        byte = 0b10000000 | byte
    return value, byte

def encode_int(value, max_size=None):
    data = []
    if max_size is None:
        while value != 0:
            value, byte = encode_step_int(value)
            data.append(byte)
    else:
        for offset in range(0, max_size+1, 7):
            value, byte = encode_step_int(value)
            data.append(byte)
            if value == 0: break
        else:
            raise ValueError("Int is too big")
    return bytearray(data)

def varint_to_data(value):
    return encode_int(value, max_size=35)
        

def string_from_data(data, current=0):
    length, next_bit = varint_from_data(data, current=current)
    string = data[next_bit:next_bit+length].decode()
    return string, next_bit+length

def string_to_data(string):
    string = string.encode()
    length = varint_to_data(len(string))
    return length + string