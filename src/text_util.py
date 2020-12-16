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
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel

"""

"""

import numpy as np


def string_to_blocks(text: str, block_size: int) -> np.ndarray:
    return reshape_blocks(blocks=[ord(c) for c in text], block_size=block_size)


def text_blocks(text: str, block_size: int) -> str:
    i = 0
    while i < len(text):
        yield "".join(text[i: i + block_size])
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


def ascii_file_to_blocks(filename: str) -> np.ndarray:
    with open(filename, "r") as fin:
        text = fin.read()
    return reshape_blocks(blocks=[ord(c) for c in text])


def chr_decode(c) -> str:
    try:
        return chr(c)
    except Exception:
        return ""


def text_file_to_blocks(filename: str, encoding: str = "utf-8") -> list:
    """
        letters to numbers

    :param filename:
    :param encoding:
    :return:
    """
    if encoding == "ascii":
        return ascii_file_to_blocks(filename)
    end = 4 if encoding == "utf-16" else 16
    with open(filename, "rb") as fin:
        while letters := fin.read(end):
            len_byte = len(letters)
            content = [number for number in letters]
            if len_byte < end:
                # when you have to fill up, it means you've reached eof
                content.extend([0] * (end - len_byte))
            yield content
