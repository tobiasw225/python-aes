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

import re
import numpy as np
import binascii
import os


from itertools import cycle
from functools import partial
from typing import List, Iterable


def string_to_blocks(text: str, block_size: int) -> np.ndarray:
    return reshape_blocks(blocks=[ord(c) for c in text], block_size=block_size)


def text_blocks(text: str, block_size: int) -> str:
    i = 0
    while i < len(text):
        yield "".join(text[i : i + block_size])
        i += block_size


def reshape_blocks(blocks: list, block_size: int = 16) -> np.ndarray:
    """
        reshape blocks from simple list
        to list of lists and add a default-value
        (whitespace : 32)

    :param blocks:
    :param block_size:
    :return:
    """
    future_len = len(blocks) + block_size - (len(blocks) % block_size)
    n_rows = future_len // block_size
    new_blocks = np.full(future_len, dtype=int, fill_value=32)
    new_blocks[: len(blocks)] = blocks
    return new_blocks.reshape((n_rows, block_size))


def chr_decode(c) -> str:
    try:
        return chr(c)
    except Exception:
        return ""


def ascii_file_to_blocks(filename: str) -> np.ndarray:
    with open(filename, "r") as fin:
        text = fin.read()
    return reshape_blocks(blocks=[ord(c) for c in text])


def utf_text_file_to_blocks(filename: str, encoding: str = "utf-8") -> list:
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


def generate_nonce(d_type, block_size: int = 16):
    my_nonce = list(np.random.randint(0, 255, block_size))
    if d_type == "int":
        return my_nonce
    elif d_type == "str":
        return hex_string(my_nonce)


rand_key = partial(generate_nonce, "str")


def process_block(block: str) -> List:
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


def chunks(blocks, n: int = 16) -> List:
    """
        Yield successive n-sized chunks from blocks.

    :param blocks:
    :param n:
    :return:
    """
    for i in range(0, len(blocks), n):
        yield blocks[i: i + n]


def xor(data: str, key: str) -> List:
    return [a ^ b for (a, b) in zip(bytes(data, "utf-8"), cycle(bytes(key, "utf-8")))]


def rstrip(value, l: list) -> List:
    while l[-1] == value:
        l.pop(-1)
    return l


remove_trailing_zero = partial(rstrip, 0)


"""
    byte utils
"""


def fill_byte_block(block: Iterable, block_size: int) -> List:
    block = [number for number in block]
    block.extend([0] * (block_size - len(block)))
    return block


def blocks_of_file(filename: str, block_size: int = 16) -> np.ndarray:
    assert os.path.isfile(filename)
    with open(file=filename, mode="rb") as fin:
        while block := fin.read(block_size):
            yield np.array(fill_byte_block(block, block_size))


def blocks_of_string(text: str, block_size: int = 16) -> np.ndarray:
    text = bytes(text, "utf-8")
    for i, block in enumerate(chunks(text, n=block_size)):
        yield bytes(fill_byte_block(block, block_size)).decode("utf-8")


def block_to_byte(block) -> bytes:
    b_block = [hex(number)[2:].zfill(2) for number in block]
    return binascii.unhexlify("".join(b_block))
