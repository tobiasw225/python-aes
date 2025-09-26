from typing import List


def _get_row(block: List[int], i: int, num_rows: int) -> (List[int], List[int]):
    """
    get values and indices of row with index i
    comment: looks a little bit like columns, but I think this
    does not matter.
    """
    row, indices = [0] * num_rows, [0] * num_rows
    row_index = 0
    block_index = i
    end_index = block_index + 16
    while block_index < end_index:
        row[row_index] = block[block_index]
        indices[row_index] = block_index
        row_index += 1
        block_index += num_rows
    return row, indices


def shift_down_index_by_row(
    indices: List[int], block_size: int, num_rows: int
) -> List[int]:
    new_indices = [x + num_rows for x in indices]
    # Correct mistakes if the index overflows to the right.
    new_indices = [x - block_size if x > block_size else x for x in new_indices]
    return new_indices


def shift_up_index_by_row(
    indices: List[int], num_rows: int, block_size: int
) -> List[int]:
    new_indices = [x - num_rows for x in indices]
    # Correct mistakes if the index overflows to the right.
    new_indices = [x + block_size if x < 0 else x for x in new_indices]
    return new_indices


def _shift_block(
    block: List[int], invert: bool, row_number: int, num_rows: int, block_size: int
) -> List[int]:
    row, indices = _get_row(block, row_number, num_rows=num_rows)
    if not invert:
        shifted_indices = shift_up_index_by_row(
            indices, num_rows=num_rows, block_size=block_size
        )
    else:
        shifted_indices = shift_down_index_by_row(
            indices, num_rows=num_rows, block_size=block_size
        )
    # Assigning of the values of the row to the original array
    for new_index, digit in zip(shifted_indices, row):
        block[new_index] = digit
    return block


def shift(
    block: List[int], num_rows: int, block_size: int, invert: bool = False
) -> List[int]:
    """
    >>> _block = [  0,  17,  34,  51,  68,  85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]
    >>> shift(_block)  # doctest: +NORMALIZE_WHITESPACE
    [0, 85, 170, 255, 68, 153, 238, 51, 136, 221, 34, 119, 204, 17, 102, 187]
    >>> shift(_block, invert=True) # doctest: +NORMALIZE_WHITESPACE
    [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]

    :param block_size:
    :param num_rows:
    :param block:
    :param invert:
    :return:
    """
    for row_number in range(1, num_rows):
        # the second row does this once, the third twice, and so on.
        for _ in range(row_number):
            block = _shift_block(
                block=block,
                invert=invert,
                row_number=row_number,
                num_rows=num_rows,
                block_size=block_size,
            )
    return block
