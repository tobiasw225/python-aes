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
from res.mixColTables import *


def mix_column(col: list) -> list:
    """

    :param col:
    :return:
    """
    b0 = m2[col[0]] ^ m3[col[1]] ^ col[2] ^ col[3]
    b1 = col[0] ^ m2[col[1]] ^ m3[col[2]] ^ col[3]
    b2 = col[0] ^ col[1] ^ m2[col[2]] ^ m3[col[3]]
    b3 = m3[col[0]] ^ col[1] ^ col[2] ^ m2[col[3]]
    return [b0, b1, b2, b3]


def mix_column_inv(col: list) -> list:
    """

    :param col:
    :return:
    """
    r0 = m14[col[0]] ^ m11[col[1]] ^ m13[col[2]] ^ m9[col[3]]
    r1 = m9[col[0]] ^ m14[col[1]] ^ m11[col[2]] ^ m13[col[3]]
    r2 = m13[col[0]] ^ m9[col[1]] ^ m14[col[2]] ^ m11[col[3]]
    r3 = m11[col[0]] ^ m13[col[1]] ^ m9[col[2]] ^ m14[col[3]]
    return [r0, r1, r2, r3]


def mix_columns(block: np.ndarray) -> np.ndarray:
    """
    # MIT S-Alle Spalten (?)
    @todo doc

    :param block:
    :return:
    """
    for row in np.arange(16).reshape((4, 4)):
        block[row] = mix_column(block[row])
    return block


def mix_columns_inv(block: np.ndarray) -> np.ndarray:
    """
    @todo doc

    :param block:
    :return:
    """
    for row in np.arange(16).reshape((4, 4)):
        # insert column.
        block[row] = mix_column_inv(block[row])

    return block

