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
import os
import re
from functools import partial
from itertools import cycle

import numpy as np


def hex_string(block):
    return "".join(str(format(sign, "02x")) for sign in block)


def generate_nonce(d_type, block_size: int = 16):
    """

    :param d_type:
    :param block_size:
    :return:
    """
    my_nonce = list(np.random.randint(0, 255, block_size))
    if d_type == "int":
        return my_nonce
    elif d_type == "str":
        return hex_string(my_nonce)


rand_key = partial(generate_nonce, "str")


def process_block(block: str) -> np.ndarray:
    """

    :param block:
    :return:
    """
    block = re.findall("..", block)  # splits the string in 2pairs
    return np.array(list(map(lambda x: int(x, 16), block)), dtype=int)


def get_key(key: str) -> np.ndarray:
    """

    :param key:
    :return:
    """
    if os.path.isfile(key):
        with open(key, "r") as f:
            key = f.read()
    return np.array(process_block(key))


get_block = get_key


def chunks(blocks, n: int = 16):
    """
        Yield successive n-sized chunks from blocks.

    :param blocks:
    :param n:
    :return:
    """
    for i in range(0, len(blocks), n):
        yield blocks[i: i + n]


def xor(data, key):
    return [a ^ b for (a, b) in zip(bytes(data, "utf-8"),
                                    cycle(bytes(key, "utf-8")))]


def sample_nonce(block_size):
    _nonce = np.zeros(block_size, dtype=int)
    _nonce[: block_size // 2] = generate_nonce(d_type="int",
                                               block_size=block_size // 2)
    return _nonce
