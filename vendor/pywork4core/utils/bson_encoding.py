"""
This module provides functions to encode bad characters before saving
them to MongoDB.
"""
from functools import partial


__all__ = [
    "encode_field_name", "decode_field_name",
    "encode_dict", "decode_dict",
]


ENCODING = (
    ('%', '%37'),
    ('.', '%46'),
    ('$', '%36'))

R_ENCODING = tuple(reversed([(y, x) for x, y in ENCODING]))


def _encode(encoding, string):
    """
    Subrouting to encode a string using an iterable of tuples.
    """
    for search, replace in encoding:
        string = string.replace(search, replace)
    return string


def _encode_dict(encoder, dictionary):
    """
    Subrouting to encode a dictionary using an iterable of tuples.
    """
    if not isinstance(dictionary, dict):
        return dictionary

    return {encoder(key): _encode_dict(encoder, value) for key, value in dictionary.iteritems()}


encode_field_name = partial(_encode, ENCODING)  # pylint: disable=invalid-name
decode_field_name = partial(_encode, R_ENCODING)  # pylint: disable=invalid-name
encode_dict = partial(_encode_dict, encode_field_name)  # pylint: disable=invalid-name
decode_dict = partial(_encode_dict, decode_field_name)  # pylint: disable=invalid-name
