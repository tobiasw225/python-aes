#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: aes256.py
#
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel
from typing import List

from steps import add_roundkey, mix_columns, mix_columns_inv, shift_block
from tables import sbox, sbox_inv


def encrypt(block: List, expanded_key: List) -> List:
    """
    >>> key = [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9,\
     10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,\
      25, 26, 27, 28, 29, 30, 31]
    >>> block = [  0,  17,  34,  51,  68,  85, 102, 119,\
     136, 153, 170, 187, 204, 221, 238, 255]
    >>> enc = encrypt(block=block,expanded_key=key)
    >>> dec = decrypt(block=enc,expanded_key=key)
    >>> print(dec.__repr__())
    [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]

    :param block:
    :param expanded_key:
    :return: encrypted array
    """
    for i in range(15):
        ri = expanded_key[i : i + 16]
        if i != 0:
            block = [sbox[z] for z in block]
            block = shift_block(block)
            if i != 14:
                block = mix_columns(block)
        block = add_roundkey(block=block, round_key=ri)
    return block


def decrypt(block: List, expanded_key: List) -> List:
    """
    >>> key = [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10,\
     11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,\
      27, 28, 29, 30, 31]
    >>> enc = [  0,  17,  34,  51,  68,  85, 102, 119, 136,\
     153, 170, 187, 204, 221, 238, 255]
    >>> dec = decrypt(block=enc,expanded_key=key)
    >>> enc = encrypt(block=dec,expanded_key=key)
    >>> print(enc.__repr__()) # doctest: +NORMALIZE_WHITESPACE
    [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]

    :param block:
    :param expanded_key:
    :return: decrypted array
    """
    for i in range(14, -1, -1):
        ri = expanded_key[i : i + 16]
        if i == 14:
            block = add_roundkey(block=block, round_key=ri)
        else:
            block = shift_block(block, invert=True)
            block = [sbox_inv[z] for z in block]
            block = add_roundkey(block=block, round_key=ri)
            if i != 0:
                block = mix_columns_inv(block)
    return block
