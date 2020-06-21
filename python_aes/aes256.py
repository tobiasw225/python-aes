#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: aes256.py
#
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel

import numpy as np
from python_aes.add_round_key import add_roundkey
from python_aes.column_mixer import mix_columns_inv, mix_columns
from python_aes.key_manager import create_round_key
from python_aes.row_shifter import shift_block
from python_aes.sbox import sbox
from python_aes.sbox_inv import sbox_inv


def encrypt(block: np.ndarray, expanded_key: np.ndarray) -> np.ndarray:
    """
    >>> key = np.array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9,\
     10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,\
      25, 26, 27, 28, 29, 30, 31])
    >>> block = np.array([  0,  17,  34,  51,  68,  85, 102, 119,\
     136, 153, 170, 187, 204, 221, 238, 255])
    >>> enc = encrypt(block=block,expanded_key=key)
    >>> dec = decrypt(block=enc,expanded_key=key)
    >>> print(dec.__repr__())
    array([  0,  17,  34,  51,  68,  85, 102, 119, 136, 153, 170, 187, 204,
           221, 238, 255])

    :param block:
    :param expanded_key:
    :return: encrypted array
    """
    for i in range(15):
        ri = create_round_key(expanded_key, i)
        if i != 0:
            block = sbox[block]
            block = shift_block(block)
            if i != 14:
                block = mix_columns(block)
        block = add_roundkey(block, ri)
    return block


def decrypt(block: np.ndarray, expanded_key: np.ndarray) -> np.ndarray:
    """
    >>> key = np.array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10,\
     11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,\
      27, 28, 29, 30, 31])
    >>> enc = np.array([  0,  17,  34,  51,  68,  85, 102, 119, 136,\
     153, 170, 187, 204, 221, 238, 255])
    >>> dec = decrypt(block=enc,expanded_key=key)
    >>> enc = encrypt(block=dec,expanded_key=key)
    >>> print(enc.__repr__()) # doctest: +NORMALIZE_WHITESPACE
    array([  0,  17,  34,  51,  68,  85, 102, 119, 136,
     153, 170, 187, 204, 221, 238, 255])

    :param block:
    :param expanded_key:
    :return: decrypted array
    """
    for i in range(14, -1, -1):
        ri = create_round_key(expanded_key, i)
        if i == 14:
            block = add_roundkey(block, ri)
        else:
            block = shift_block(block, invert=True)
            block = sbox_inv[block]
            block = add_roundkey(block, ri)
            if i != 0:
                block = mix_columns_inv(block)
    return block
