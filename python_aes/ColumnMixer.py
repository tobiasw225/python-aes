#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: ColumnMixer.py
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
four_by_four_mat = np.arange(16).reshape((4, 4))


def mix_columns(block: np.ndarray) -> np.ndarray:
    """
    @todo doc

    :param block:
    :return:
    """
    return np.array(
        [mix_column(block[row]) for row in four_by_four_mat], dtype=int
    ).reshape(-1)


def mix_columns_inv(block: np.ndarray) -> np.ndarray:
    """
    @todo doc

    :param block:
    :return:
    """
    return np.array(
        [mix_column_inv(block[row]) for row in four_by_four_mat], dtype=int
    ).reshape(-1)
