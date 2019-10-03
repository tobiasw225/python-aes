#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: helper.py
#
# __description__:
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel

import random
import re
import numpy as np


def print_block(block: list):
    """

    :param block:
    :return:
    """
    for i in range(0, 16, 4):
        print("\t".join(block[i:i+4]))
        print("\n")


def rand_key() -> str:
    """

    :return:
    """
    rk = np.random.randint(0, 255, 32)
    rk = [format(i,  '02x') for i in rk]
    return "".join(rk)


def fmap(x):
    """

    :param x:
    :return:
    """
    return int(x, 16)


def process_block(block: str) -> np.ndarray:
    """

    :param block:
    :return:
    """
    block = re.findall('..', block)  # splits the string in 2pairs
    return np.array(list(map(fmap, block)), dtype=int)


def get_key(file: str) -> np.ndarray:
    """

    :param file:
    :return:
    """
    with open(file, "r") as f:
        return np.array(process_block(f.read()))


get_block = get_key


def chunks(blocks, n: int = 16):
    """
        Yield successive n-sized chunks from blocks.

    :param blocks:
    :param n:
    :return:
    """
    for i in range(0, len(blocks), n):
        yield blocks[i:i + n]