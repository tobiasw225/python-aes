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
    assert len(block) == len(round_key)
    return np.bitwise_xor(round_key, block)
