#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: add_roundkey.py
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


def add_roundkey(round_key: np.ndarray, block: np.ndarray) -> np.ndarray:
    """

    :param round_key:
    :param block:
    :return:
    """
    assert len(block) == len(round_key)
    return np.array([rk ^ b for rk, b in zip(round_key, block)])
