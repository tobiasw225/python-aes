#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: keyManager.py
#
# __description__:
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel

import numpy as np

from python_aes.res.rcon import *
from python_aes.res.sbox import *


def key_schedule_core(word: np.ndarray, it_no: int) -> list:
    """

    :param word:
    :param it_no:
    :return:
    """
    # inserting the values to the new places
    word = np.roll(word, -1)
    # apply sbox
    word = sbox[word]
    # perform the rcon operation with i as the input,
    # and exclusive or the rcon output with the first byte of the output word
    word[0] ^= rcon[it_no]
    return word


def expand_key(key: list) -> np.ndarray:
    """

    :param key:
    :return:
    """
    c = 32
    i = 1

    while c < 240:
        # Copy the temporary variable over
        word = np.array(key[c-4: c])
        # Every eight sets, do a complex calculation
        if c % 32 == 0:
            word = key_schedule_core(word, i)
            i += 1
            # For 256-bit keys, we add an extra sbox to the calculation
        if c % 32 == 16:
            word = sbox[word]

        for a in range(4):
            key.append([])  # array needs to be extended
            key[c] = key[c - 32] ^ word[a]  # appending
            c += 1
    return np.array(key)


def create_round_key(expanded_key: np.ndarray, n: int) -> np.ndarray:
    """

    :param expanded_key:
    :param n:
    :return:
    """
    return expanded_key[n:n+16]
