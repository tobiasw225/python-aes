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
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel


# from __future__ import division, absolute_import
# from __future__ import print_function, unicode_literals

from python_aes.ColumnMixer import *
from python_aes.row_shifter import *
from python_aes.key_manager import *
from python_aes.add_round_key import add_roundkey
from sbox_inv import *
from sbox import *


def encrypt(block: np.ndarray,
            expanded_key: np.ndarray) -> np.ndarray:
    """

    :param block:
    :param expanded_key:
    :return:
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


def decrypt(block: np.ndarray,
            expanded_key: np.ndarray) -> np.ndarray:
    """

    :param block:
    :param expanded_key:
    :return:
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

