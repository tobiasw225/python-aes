#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: text_encoding.py
#
# __description__: Functions to convert the given Text to numbers
#         and following that converting them to block of the
#         size of 16 numbers
#
#         Decoding Function which can be used to derive a text out of a given
#         (decoded) block.
#
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel

"""

"""
import binascii
import os
import random
import re
from functools import partial
from itertools import cycle
from typing import Iterable, List, Union, Any


def text_to_ord(text: str) -> List[int]:
    return [ord(c) for c in text]


def string_to_blocks(text: str, block_size: int) -> List:
    return reshape_blocks(blocks=text_to_ord(text), block_size=block_size)


def text_blocks(text: str, block_size: int) -> str:
    i = 0
    while i < len(text):
        yield "".join(text[i : i + block_size])
        i += block_size


def reshape_blocks(blocks: list, block_size: int = 16) -> List:
    """
        reshape blocks from simple list
        to list of lists and add a default-value
        (whitespace : 32)

    :param blocks:
    :param block_size:
    :return:
    """
    start = 0
    while len(row := blocks[start : start + block_size]) == block_size:
        yield row
        start += block_size
    # last row might not be full
    last_row = [32] * block_size
    for i in range(len(row)):
        last_row[i] = row[i]
    yield last_row


def chr_decode(c) -> str:
    try:
        return chr(c)
    except Exception:
        return ""


def xor_blocks(a: Iterable, b: Iterable) -> Iterable:
    return [l ^ d for l, d in zip(a, b)]


def ascii_file_to_blocks(filename: str) -> Iterable:
    with open(filename, "r") as fin:
        text = fin.read()
    return reshape_blocks(blocks=text_to_ord(text))


def utf_text_file_to_blocks(filename: str, encoding: str = "utf-8") -> List[int]:
    """
        letters to numbers

    :param filename:
    :param encoding:
    :return:
    """
    end = 4 if encoding == "utf-16" else 16
    with open(filename, "rb") as fin:
        while letters := fin.read(end):
            len_byte = len(letters)
            content = [number for number in letters]
            if len_byte < end:
                # when you have to fill up, it means you've reached eof
                content.extend([0] * (end - len_byte))
            yield content


def hex_string(block) -> str:
    return "".join(str(format(sign, "02x")) for sign in block)


def generate_nonce(d_type, block_size: int = 16) -> Union[List[int], str]:
    my_nonce = list(random_ints(block_size, 0, 255))
    if d_type == "int":
        return my_nonce
    elif d_type == "str":
        return hex_string(my_nonce)


rand_key = partial(generate_nonce, "str")


def process_block(block: str) -> List[int]:
    """
        splits the string in 2pairs
        ...
    :param block:
    :return:
    """
    block = re.findall("..", block)
    return list(map(lambda x: int(x, 16), block))


def hex_digits_to_block(key: str) -> List:
    if os.path.isfile(key):
        with open(key, "r") as f:
            key = f.read()
    elif type(key) is not str:
        raise ValueError("Key must be valid path or str.")
    return process_block(key)


def chunks(blocks: Iterable, n: int = 16) -> Iterable:
    """
        Yield successive n-sized chunks from blocks.

    :param blocks:
    :param n:
    :return:
    """
    for i in range(0, len(blocks), n):
        yield blocks[i: i + n]


def rstrip_value(value: Any, my_list: List[Any]) -> List[Any]:
    while my_list[-1] == value:
        my_list.pop(-1)
    return my_list


remove_trailing_zero = partial(rstrip_value, 0)


"""
    byte utils
"""


def fill_byte_block(block: Iterable, block_size: int) -> List:
    block = [number for number in block]
    block.extend([0] * (block_size - len(block)))
    return block


def blocks_of_file(filename: str, block_size: int = 16) -> List:
    with open(file=filename, mode="rb") as fin:
        while block := fin.read(block_size):
            yield fill_byte_block(block, block_size)


def blocks_of_string(text: str, block_size: int = 16) -> bytes:
    text = bytes(text, "utf-8")
    for i, block in enumerate(chunks(text, n=block_size)):
        yield bytes(fill_byte_block(block, block_size)).decode("utf-8")


def block_to_byte(block) -> bytes:
    b_block = [hex(number)[2:].zfill(2) for number in block]
    return binascii.unhexlify("".join(b_block))


def random_ints(n: int, start: int = 0, stop: int = -1) -> List[int]:
    gen = random.SystemRandom()
    return [gen.randrange(start=start, stop=stop) for _ in range(n)]
