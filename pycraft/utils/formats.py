def varint_from_data(data, current=0):
    value = 0
    for offset in range(0,36,7):
        value |= (data[current] & 0b01111111) << offset
        if (data[current] & 0b10000000) == 0:
            return value, current + 1
        current += 1
    else:
        raise ValueError("VarInt is too big")

def varint_to_data(value):
    data = []
    for offset in range(0, 36, 7):
        byte = value & 0b01111111
        value = value >> 7
        if (value == 0):
            data.append(byte)
            break
        else:
            data.append(0b10000000 | byte)
    else:
        raise ValueError("VarInt is too big")
    return bytearray(data)
        

def string_from_data(data, current=0):
    length, next_bit = varint_from_data(data, current=current)
    string = data[next_bit:next_bit+length].decode()
    return string, next_bit+length

def string_to_data(string):
    string = string.encode()
    length = varint_to_data(len(string))
    return length + string