import math

from random import getrandbits, randrange, randint

SMALL_PRIMES = []

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
        s //= 2
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
    p = getrandbits(bits)
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

def genrsakeypair(bits=1024):
    p, q = getrandprime(bits), getrandprime(bits)
    n = p * q
    lambda_n = math.lcm(p - 1, q - 1)
    e = gencoprime(lambda_n)
    d = pow(e, -1, lambda_n)
