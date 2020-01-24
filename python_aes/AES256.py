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
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel


from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

from python_aes.ColumnMixer import *
from python_aes.RowShifter import *
from python_aes.keyManager import *
from python_aes.AddRoundKey import add_roundkey
from sboxInv import *
from sbox import *


def encrypt(block: np.ndarray,
            expanded_key: np.ndarray) -> np.ndarray:
    """

    :param block:
    :param expanded_key:
    :return:
    """
    for i in range(15):
        if i == 0:
            r0 = create_round_key(expanded_key, 0)
            block = add_roundkey(block=block, round_key=r0)

        elif i == 14:
            r14 = create_round_key(expanded_key, 14)
            block = sbox[block]
            block = shift_block(block)
            block = add_roundkey(block, r14)
        else:
            ri = create_round_key(expanded_key, i)
            block = sbox[block]
            block = shift_block(block)
            block = mix_columns(block)
            block = add_roundkey(block, ri)

    return block


def decrypt(block: np.ndarray,
            expanded_key: np.ndarray) -> np.ndarray:
    """

    :param block:
    :param expanded_key:
    :return:
    """
    for i in range(14, -1, -1):
        if i == 14:
            r14 = create_round_key(expanded_key, 14)
            block = add_roundkey(block, r14)

        elif i == 0:
            r0 = create_round_key(expanded_key, 0)
            block = shift_block(block, invert=True)
            block = sbox_inv[block]
            block = add_roundkey(block, r0)
        else:
            ri = create_round_key(expanded_key, i)
            block = shift_block(block, invert=True)
            block = sbox_inv[block]
            block = add_roundkey(block, ri)
            block = mix_columns_inv(block)
    return block

