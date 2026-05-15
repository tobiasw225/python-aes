def _get_row(block: list[int], i: int, num_rows: int) -> tuple[list[int], list[int]]:
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
    indices: list[int], block_size: int, num_rows: int
) -> list[int]:
    new_indices = [x + num_rows for x in indices]
    return [x - block_size if x > block_size else x for x in new_indices]


def shift_up_index_by_row(
    indices: list[int], num_rows: int, block_size: int
) -> list[int]:
    new_indices = [x - num_rows for x in indices]
    # Correct mistakes if the index overflows to the right.
    return [x + block_size if x < 0 else x for x in new_indices]


def _shift_block(
    block: list[int], invert: bool, row_number: int, num_rows: int, block_size: int
) -> list[int]:
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
    for new_index, digit in zip(shifted_indices, row, strict=False):
        block[new_index] = digit
    return block


def shift(
    block: list[int], num_rows: int, block_size: int, invert: bool = False
) -> list[int]:
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
