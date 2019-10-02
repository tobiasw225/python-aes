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


def print_block(block: list):
    """

    :param block:
    :return:
    """
    i = 0
    for u in range(4):
        for j in range(i, i+4):
            print(block[j], end='\t')
        i += 4
        print("\n")


def rand_key() -> str:
    """

    :return:
    """
    rk = [''] * 32
    for i in range(32):
        number = random.randint(0, 0xFF)
        number = format(number, '02x')
        rk[i] = number
    return "".join(rk)


def fmap(x):
    """

    :param x:
    :return:
    """
    return int(x, 16)


def process_block(block: str) -> list:
    """

    :param block:
    :return:
    """
    block = re.findall('..', block)  # splits the string in 2pairs
    return list(map(fmap, block))


def get_key(file: str) -> list:
    """

    :param file:
    :return:
    """
    with open(file, "r") as f:
        return process_block(f.read())

def chunks(blocks, n: int = 16):
    """
        Yield successive n-sized chunks from blocks.

    :param blocks:
    :param n:
    :return:
    """
    for i in range(0, len(blocks), n):
        yield blocks[i:i + n]