#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: readBlockFile.py
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
from python_aes.helper import process_block


def get_blocks(file: str) -> list:
    """

    :param file:
    :return:
    """
    blocks = []
    with open(file, "r") as fin:
        for block in fin:
            block = process_block(block)
            # if the block is less than 16 signs long append 0s
            while len(block) < 16:
                block.append(0)
            blocks.append(block)

    return blocks


