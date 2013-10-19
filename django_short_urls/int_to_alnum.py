# coding=utf-8

"""Converts an integer to an alphanumerical string"""

from __future__ import unicode_literals

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


def encode(decoded, alphabet=ALPHABET):
    """Converts an int to an alphanumerical string"""

    if decoded == 0:
        return alphabet[0]

    base = len(alphabet)
    encoded = []

    while decoded:
        encoded.append(alphabet[decoded % base])
        decoded = decoded // base

    encoded.reverse()
    return ''.join(encoded)


def decode(encoded, alphabet=ALPHABET):
    """Converts an alphanumerical string to an int"""

    base = len(alphabet)
    decoded = 0
    power = 1

    encoded = list(encoded)
    encoded.reverse()

    for char in encoded:
        decoded += alphabet.index(char) * power
        power *= base

    return decoded


if __name__ == "__main__":
    TEST = 123456789

    print "Test: %d == %d" % (TEST, decode(encode(TEST)))
