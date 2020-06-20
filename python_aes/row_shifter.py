#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: row_shifter.py
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


def shift_block(block: np.ndarray, invert: bool = False) -> np.ndarray:
    """
    @todo doc

    :param block:
    :param invert:
    :return:
    """
    temp_arr = np.zeros(4, dtype=int)
    indices = np.zeros(4, dtype=int)

    # Loop for Iteration of each row (2nd, 3rd, 4th)
    for row in range(1, 4):

        for i in range(row):
            # Get the elements of the row
            i = row
            j = 0

            while i < 16:
                # save digits of block
                # as well as positions
                temp_arr[j] = block[i]
                indices[j] = i
                j += 1
                i += 4

            if not invert:
                #  Every index is subtracted by 4 to get the new one
                new_indices = indices - 4
                new_indices[new_indices < 0] += 16
            else:
                # Every index is added by 4 to get the new one
                new_indices = indices + 4
                new_indices[new_indices > 16] -= 16

            # Assigning of the values of the row to the original array
            for z, digit in zip(new_indices, temp_arr):
                block[z] = digit

    return np.array(block)
