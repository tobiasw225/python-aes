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
from typing import List

from tables import rcon, sbox


def key_schedule_core(word: List[int], iteration: int) -> List[int]:
    """

    :param word:
    :param iteration:
    :return:
    """
    # inserting the values to the new places
    # (shift left)
    word.append(word.pop(0))
    # apply sbox
    word = [sbox[i] for i in word]
    # perform the rcon operation with i as the input,
    # and exclusive or the rcon output with the first byte of the output word
    word[0] ^= rcon[iteration]
    return word


def expand_key(key: List[int]) -> List[int]:
    """
    >>> key = [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, \
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,\
     27, 28, 29, 30, 31]
    >>> res = expand_key(key)
    >>> res
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 41, 115, 194, 159, 45, 118, 196, 152, 37, 127, 206, 147, 41, 114, 192, 156, 181, 81, 168, 205, 161, 68, 190, 218, 185, 93, 164, 193, 165, 64, 186, 222, 173, 135, 223, 153, 128, 241, 27, 1, 165, 142, 213, 146, 140, 252, 21, 14, 209, 225, 241, 102, 112, 165, 79, 188, 201, 248, 235, 125, 108, 184, 81, 163, 76, 86, 213, 201, 204, 167, 206, 200, 105, 41, 27, 90, 229, 213, 14, 84, 8, 226, 90, 70, 120, 71, 21, 250, 177, 191, 254, 135, 221, 7, 175, 36, 4, 47, 227, 8, 200, 136, 45, 192, 161, 161, 54, 154, 68, 116, 56, 206, 19, 112, 93, 205, 107, 55, 72, 55, 218, 136, 182, 176, 7, 143, 25, 148, 250, 251, 193, 205, 50, 115, 236, 13, 147, 210, 218, 151, 215, 166, 226, 89, 29, 84, 197, 6, 118, 99, 141, 49, 172, 235, 59, 129, 171, 100, 34, 21, 52, 104, 152, 175, 6, 27, 116, 162, 149, 201, 174, 53, 66, 111, 76, 108, 49, 252, 236, 86, 71, 159, 97, 103, 235, 116, 90, 230, 64, 16, 120, 243, 115, 212, 149, 166, 117, 207, 225, 4, 224, 6, 79, 49, 162, 105, 3, 93]

    :param key:
    :return:
    """
    # initialize extended key with key-elements.
    c = 32
    expanded_key = [0] * 240
    expanded_key[:len(key)] = key

    while c < 240:
        # Copy the temporary variable.
        word = expanded_key[c - 4 : c]
        if c % 32 == 0:
            # Every eight sets, do a complex calculation.
            # (c % 32)-1 ~ i+1
            word = key_schedule_core(word, (c % 32) - 1)
        if c % 32 == 16:
            # For 256-bit keys, we add an extra sbox to the calculation.
            word = [sbox[i] for i in word]
        key_row = expanded_key[c - 32 : c + 4 - 32]
        expanded_key[c : c + 4] = [k ^ w for k, w in zip(key_row, word)]
        c += 4
    return expanded_key
