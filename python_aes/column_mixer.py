#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: column_mixer.py
#
# __description__:
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel
# flake8: noqa

import numpy as np

from python_aes.mix_col_tables import *


def mix_column(col: list) -> np.ndarray:
    """

    :param col:
    :return:
    """
    b0 = m2[col[0]] ^ m3[col[1]] ^ col[2] ^ col[3]
    b1 = col[0] ^ m2[col[1]] ^ m3[col[2]] ^ col[3]
    b2 = col[0] ^ col[1] ^ m2[col[2]] ^ m3[col[3]]
    b3 = m3[col[0]] ^ col[1] ^ col[2] ^ m2[col[3]]
    return np.array([b0, b1, b2, b3], dtype=int)


def mix_column_inv(col: list) -> np.ndarray:
    """

    :param col:
    :return:
    """
    r0 = m14[col[0]] ^ m11[col[1]] ^ m13[col[2]] ^ m9[col[3]]
    r1 = m9[col[0]] ^ m14[col[1]] ^ m11[col[2]] ^ m13[col[3]]
    r2 = m13[col[0]] ^ m9[col[1]] ^ m14[col[2]] ^ m11[col[3]]
    r3 = m11[col[0]] ^ m13[col[1]] ^ m9[col[2]] ^ m14[col[3]]
    return np.array([r0, r1, r2, r3], dtype=int)


# this matrix makes looping way easier.
four_by_four_mat = np.array([[ 0,  1,  2,  3],
       [ 4,  5,  6,  7],
       [ 8,  9, 10, 11],
       [12, 13, 14, 15]])


def mix_columns(block: np.ndarray) -> np.ndarray:
    """
    >>> block = np.array([  0,  17,  34,  51,  68,  85, 102, 119,\
     136, 153, 170, 187, 204, 221, 238, 255])
    >>> mix_columns(block)
    array([ 34, 119,   0,  85, 102,  51,  68,  17, 170, 255, 136, 221, 238,
           187, 204, 153])

    """
    return np.array(
        [mix_column(block[row]) for row in four_by_four_mat], dtype=int
    ).reshape(-1)


def mix_columns_inv(block: np.ndarray) -> np.ndarray:
    """
    >>> block = np.array([  0,  17,  34,  51,  68,  85, 102, 119,\
     136, 153, 170, 187, 204, 221, 238, 255])
    >>> mix_columns_inv(block)
    array([170, 255, 136, 221, 238, 187, 204, 153,  34, 119,   0,  85, 102,
            51,  68,  17])
    >>> all(mix_columns_inv(mix_columns(block)) == block)
    True

    """
    return np.array(
        [mix_column_inv(block[row]) for row in four_by_four_mat], dtype=int
    ).reshape(-1)