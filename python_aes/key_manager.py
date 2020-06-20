#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: key_manager.py
#
# __description__:
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel

from python_aes.rcon import *
from python_aes.sbox import *


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


def expand_key(key: np.ndarray) -> np.ndarray:
    """

    :param key:
    :return:
    """
    c = 32
    # initialize extended key with key-elements.
    _key = np.zeros(240, dtype=int)
    _key[:32] = key
    key = _key

    while c < 240:
        # Copy the temporary variable.
        word = key[c-4: c]
        if c % 32 == 0:
            # Every eight sets, do a complex calculation.
            # (c % 32)-1 ~ i+1
            word = key_schedule_core(word, (c % 32)-1)
        if c % 32 == 16:
            # For 256-bit keys, we add an extra sbox to the calculation.
            word = sbox[word]
        key[c: c + 4] = key[c-32: c+4-32] ^ word
        c += 4
    return key


def create_round_key(expanded_key: np.ndarray,
                     n: int,
                     key_length: int = 16) -> np.ndarray:
    """

    :param key_length:
    :param expanded_key:
    :param n:
    :return:
    """
    return expanded_key[n:n+key_length]
