import base64
import math

from random import randrange, randint
from secrets import randbits

import pycraft.utils.formats as formats

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
                71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 
                151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 
                233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 
                317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 
                419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 
                503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 
                607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 
                701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 
                811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 
                911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

def small_primes_check(number):
    for p in SMALL_PRIMES:
        if number % p == 0:
            return False
    return True

def miller_rabin(number, nb_trials=40):
    # I still don't know how it works, but... it works ^^
    r, s = 0, number - 1
    while s % 2 == 0:
        r += 1
        s >>= 1 # it might be quicker
        # s //= 2
    for _ in range(nb_trials):
        a = randrange(2, number - 1)
        x = pow(a, s, number)
        if x == 1 or x == number - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, number)
            if x == number - 1:
                break
        else:
            return False
    return True

def is_prime(number):
    if small_primes_check(number) and miller_rabin(number):
        return True
    return False

def getrandprimecandidate(bits=1024):
    p = randbits(bits)
    p |= (0b1 << (bits - 1) ) | 0b1 # make sur first bit is 1 so we have 1024 bits and last bit is 1 so it's an odd number
    return p

def getrandprime(bits=1024):
    p = getrandprimecandidate(bits)
    while not is_prime(p):
        p += 2
    return p

def gencoprime(number): # surement un moyen plus opti
    c = randint(0, number)
    while math.gcd(c, number) != 1:
        c = randint(0, number)
    return c


def encode_tag(tag):
    if tag < 0b00011111:
        return tag, False
    else:
        return formats.encode_int(tag - 0b00011111), True

def encode_lenght(data, indefinite=False):
    if not indefinite:
        lenght = len(data)
        if lenght <= 127:
            return int_to_bytes(lenght)
        else:
            return int_to_bytes(0b10000000 | len(int_to_bytes(lenght))) + int_to_bytes(lenght)
    else:
        return 0b10000000

def int_to_bytes(value):
    return value.to_bytes((value.bit_length() + 7) // 8, "big")

def encode_structure(data_class, data_pc, data_tag, data):
    tag, is_big = encode_tag(data_tag)
    if not is_big:
        identifier = int_to_bytes((data_class << 6) | (data_pc << 5) | tag)
    else:
        identifier = int_to_bytes((data_class << 6) | (data_pc << 5) | 0b00011111) + tag
    structure = identifier + encode_lenght(data) + data
    return identifier + encode_lenght(data) + data

def encode_oid(oid):
    ids = oid.split(".")
    data = bytearray()
    first_byte = int_to_bytes(int(ids[0])*40+int(ids[1]))
    data.extend(first_byte)
    for i in ids[2:]:
        i = int(i)
        if i <= 0b01111111:
            data.extend(int_to_bytes(i))
        else:
            value = bytearray()
            while i != 0:
                value.extend(int_to_bytes((0b01111111 & i) | 0b10000000))
                i >>= 7
            value[0] &= 0b01111111
            value.reverse()
            data.extend(bytearray(value))
    return encode_structure(0b00, 0b0, 6, data)

def encode_null():
    return (encode_structure(0b00, 0b0, 5, b"") + bytearray([0x00]))

def encode_sequence(data):
    return encode_structure(0b00, 0b1, 0x10, data)

def encode_bit_string(data):
    #TODO: vérifier qu'il n'y ai pas de bits vide devant ?
    # if len(data) % 2 == 1:
    #     data += bytearray([0x0])
    #     data = bytearray([0x8]) + data
    # else:
    #     data = bytearray([0x0]) + data
    data = bytearray([0x0]) + data
    return encode_structure(0b00, 0b0, 3, data)

def encode_integer(value):
    """ If the integer is positive but the high order bit is set to 1,
     a leading 0x00 is added to the content to indicate that the number 
     is not negative. For example, the high order byte of 0x8F (10001111)
      is 1. Therefore a leading zero byte is added to the content as shown
       in the following illustration."""
    data = int_to_bytes(value)
    if (data[0] & 0b10000000) >> 7 == 0b1:
         data = bytearray(1) + data
    return encode_structure(0b00, 0b0, 2, data)

def encode_pubkey_subject(modulus, exponent):
    return encode_sequence(
        encode_integer(modulus) + encode_integer(exponent)
    )

def encode_pubkey(modulus, exponent, algorithm):
    data = encode_sequence(
        encode_sequence(
            encode_oid(algorithm) +
            encode_null()
        ) +
        encode_bit_string(
            encode_pubkey_subject(modulus, exponent)
        )
    )
    print("LEN",len(data))
    return data

def encode_privkey(modulus, exponent):
    return

def genrsakeypair(bits=1024):
    # TODO: should be similar in magnitude but differ in length by a few digits to make factoring harder
    p, q = getrandprime(bits // 2), getrandprime(bits // 2)
    n = p * q
    lambda_n = math.lcm(p - 1, q - 1)
    # e = gencoprime(lambda_n) 
    e = 0x010001
    d = pow(e, -1, lambda_n)
    return {"d": d, "n": n}, encode_pubkey(n, e, "1.2.840.113549.1.1.1")

def remove_padding(data):
    if data[0:1] != bytearray([0x02]):
        return data
    else:
        next_byte = 1
        while data[next_byte] != 0x00:
            next_byte += 1
        return data[next_byte+1:]

def decode_with_privkey(data, d, n):
    return remove_padding(int_to_bytes(pow(int.from_bytes(data, "big"), d, n)))

def write_key(key, output, is_private=False):
    lines = []
    if not is_private:
        lines.append(b"-----BEGIN PUBLIC KEY-----")
    key = base64.b64encode(key)
    for i in range(0, len(key), 64):
        key_left = key[i:]
        if len(key_left) >= 64:
            lines.append(key_left[:64])
        else:
            lines.append(key_left)
    lines.append(b"-----END PUBLIC KEY-----")
    with open(output, "wb") as out_file:
        for line in lines:
            out_file.write(line + b"\n")
