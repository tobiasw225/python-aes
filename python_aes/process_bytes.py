#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: aes256.py
#
# __description__:
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2019
# Copyright (c) 2019 Tobias Wenzel
import os
import binascii
import numpy as np
from python_aes.helper import chunks


def fill_byte_block(block, block_size):
    block = [number for number in block]
    block.extend([0] * (block_size - len(block)))
    return block


def blocks_of_file(filename: str, block_size: int = 16) -> np.ndarray:
    """

    :param block_size:
    :param filename:
    :return:
    """
    assert os.path.isfile(filename)
    with open(file=filename, mode="rb") as fin:
        while block := fin.read(block_size):
            yield np.array(fill_byte_block(block, block_size))


def blocks_of_string(text: str, block_size: int = 16) -> np.ndarray:
    """

    :param block_size:
    :param text:
    :return:
    """
    text = bytes(text, 'utf-8')
    for i, block in enumerate(chunks(text, n=block_size)):
        yield bytes(fill_byte_block(block, block_size)).decode('utf-8')


def block_to_byte(block) -> bytes:
    """

    :param block:
    :return:
    """
    b_block = [hex(number)[2:].zfill(2) for number in block]
    return binascii.unhexlify("".join(b_block))
