from itertools import chain
from typing import List

from tables import m2, m3, m9, m11, m13, m14
from utils import chunks, xor_blocks

# todo make those parameters
NUM_ROWS = 4
BLOCK_SIZE = 16


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
    # Loop for Iteration of each row (2nd, 3rd, 4th)
    assert NUM_ROWS == 4
    for row_number in range(1, NUM_ROWS):
        # the second row does this once, the third twice, and so on.
        for _ in range(row_number):
            block = _shift_block(block, invert, row_number)
    return block


def _shift_block(block: List[int], invert: bool, row_number: int) -> List[int]:
    row, indices = get_row(block, row_number)
    if not invert:
        shifted_indices = shift_up_index_by_row(indices)
    else:
        shifted_indices = shift_down_index_by_row(indices)
    # Assigning of the values of the row to the original array
    for new_index, digit in zip(shifted_indices, row):
        block[new_index] = digit
    return block


def get_row(block: List[int], i: int) -> (List[int], List[int]):
    """
    get values and indices of row with index i
    comment: looks a little bit like columns, but I think this
    does not matter.
    """
    row, indices = [0] * NUM_ROWS, [0] * NUM_ROWS
    row_index = 0
    block_index = i
    while block_index < BLOCK_SIZE:
        row[row_index] = block[block_index]
        indices[row_index] = block_index
        row_index += 1
        block_index += NUM_ROWS
    return row, indices


def shift_down_index_by_row(indices: List[int]) -> List[int]:
    new_indices = [x + NUM_ROWS for x in indices]
    # Correct mistakes if the index overflows to the right.
    new_indices = [x - BLOCK_SIZE if x > BLOCK_SIZE else x for x in new_indices]
    return new_indices


def shift_up_index_by_row(indices: List[int]) -> List[int]:
    new_indices = [x - NUM_ROWS for x in indices]
    # Correct mistakes if the index overflows to the right.
    new_indices = [x + BLOCK_SIZE if x < 0 else x for x in new_indices]
    return new_indices


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
    return list(chain.from_iterable(mix_column(row) for row in chunks(block, n=NUM_ROWS)))


def mix_columns_inv(block: List[int]) -> List[int]:
    """
    >>> block = [  0,  17,  34,  51,  68,  85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]
    >>> mix_columns_inv(block)
    [170, 255, 136, 221, 238, 187, 204, 153, 34, 119, 0, 85, 102, 51, 68, 17]
    >>> mix_columns_inv(mix_columns(block)) == block
    True
    """
    return list(chain.from_iterable(mix_column_inv(row) for row in chunks(block, n=NUM_ROWS)))


def add_roundkey(round_key: List[int], block: List[int]) -> List[int]:
    return xor_blocks(round_key, block)
