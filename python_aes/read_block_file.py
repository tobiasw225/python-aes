#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: read_block_file.py
#
# __description__:
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel

from python_aes.helper import process_block


def get_blocks(file: str) -> list:
    """

    :param file:
    :return:
    """
    with open(file, "r") as fin:
        return [process_block(block) for block in fin]
