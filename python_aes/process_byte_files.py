#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: AES256.py
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


def blocks_of_file(filename: str, block_size: int=16) -> np.ndarray:
    """

    :param block_size:
    :param filename:
    :return:
    """
    assert os.path.isfile(filename)
    with open(file=filename, mode="rb") as fin:
        while content := fin.read(block_size):
            len_byte = len(content)
            content = [number for number in content]
            if len_byte < block_size:
                # when you have to fill up, it means you've reached eof
                content.extend([0]*(block_size-len_byte))
            yield np.array(content)

from python_aes.helper import chunks


def blocks_of_string(text: str, block_size: int=16) -> np.ndarray:
    """

    :param block_size:
    :param text:
    :return:
    """
    text = bytes(text, 'utf-8')
    for i, block in enumerate(chunks(text, n=block_size)):
        len_byte = len(block)
        block = [number for number in block]
        if len_byte < block_size:
            # when you have to fill up, it means you've reached eof
            block.extend([0]*(block_size-len_byte))
        yield block


def block_to_byte(block: np.ndarray) -> bytes:
    """

    :param block:
    :return:
    """
    b_block = [hex(number)[2:].zfill(2) for number in block]
    return binascii.unhexlify("".join(b_block))


