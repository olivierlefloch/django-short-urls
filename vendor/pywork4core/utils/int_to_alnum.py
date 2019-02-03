# coding=utf-8

"""Converts an integer to an alphanumerical string"""

from __future__ import unicode_literals

import string  # pylint: disable=deprecated-module

LOWERALPHANUM = string.digits + string.ascii_lowercase
DEFAULT_ALPHABET = LOWERALPHANUM + string.ascii_uppercase


def encode(decoded, alphabet=DEFAULT_ALPHABET):
    """Converts an int to an alphanumerical string"""

    if not decoded:
        return alphabet[0]

    base = len(alphabet)
    encoded = []

    while decoded:
        encoded.append(alphabet[decoded % base])
        decoded = decoded // base

    encoded.reverse()
    return ''.join(encoded)


def decode(encoded, alphabet=DEFAULT_ALPHABET):
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
