from itertools import chain
from typing import List

from tables import m2, m3, m9, m11, m13, m14
from utils import chunks, xor_blocks


def shift_block(block: List[int], invert: bool = False) -> List[int]:
    """
    >>> block = [  0,  17,  34,  51,  68,  85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]
    >>> shift_block(block)  # doctest: +NORMALIZE_WHITESPACE
    [0, 85, 170, 255, 68, 153, 238, 51, 136, 221, 34, 119, 204, 17, 102, 187]
    >>> shift_block(block, invert=True) # doctest: +NORMALIZE_WHITESPACE
    [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]

    :param block:
    :param invert:
    :return:
    """
    temp_arr, indices = [0] * 4, [0] * 4
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
                new_indices = map(lambda x: x - 4, indices)
                new_indices = [z + 16 if z < 0 else z for z in new_indices]
            else:
                # Every index is added by 4 to get the new one
                new_indices = map(lambda x: x + 4, indices)
                new_indices = [z - 16 if z > 16 else z for z in new_indices]
            # Assigning of the values of the row to the original array
            for z, digit in zip(new_indices, temp_arr):
                block[z] = digit
    return block


def mix_column(col: List[int]) -> List[int]:
    return [
        m2[col[0]] ^ m3[col[1]] ^ col[2] ^ col[3],
        col[0] ^ m2[col[1]] ^ m3[col[2]] ^ col[3],
        col[0] ^ col[1] ^ m2[col[2]] ^ m3[col[3]],
        m3[col[0]] ^ col[1] ^ col[2] ^ m2[col[3]],
    ]


def mix_column_inv(col: List[int]) -> List[int]:
    return [
        m14[col[0]] ^ m11[col[1]] ^ m13[col[2]] ^ m9[col[3]],
        m9[col[0]] ^ m14[col[1]] ^ m11[col[2]] ^ m13[col[3]],
        m13[col[0]] ^ m9[col[1]] ^ m14[col[2]] ^ m11[col[3]],
        m11[col[0]] ^ m13[col[1]] ^ m9[col[2]] ^ m14[col[3]],
    ]


def mix_columns(block: List[int]) -> List[int]:
    """
    >>> block = [  0,  17,  34,  51,  68,  85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]
    >>> mix_columns(block)
    [34, 119, 0, 85, 102, 51, 68, 17, 170, 255, 136, 221, 238, 187, 204, 153]

    """
    return list(chain.from_iterable(mix_column(row) for row in chunks(block, n=4)))


def mix_columns_inv(block: List[int]) -> List[int]:
    """
    >>> block = [  0,  17,  34,  51,  68,  85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]
    >>> mix_columns_inv(block)
    [170, 255, 136, 221, 238, 187, 204, 153, 34, 119, 0, 85, 102, 51, 68, 17]
    >>> mix_columns_inv(mix_columns(block)) == block
    True
    """
    return list(chain.from_iterable(mix_column_inv(row) for row in chunks(block, n=4)))


def add_roundkey(round_key: List[int], block: List[int]) -> List[int]:
    return xor_blocks(round_key, block)
