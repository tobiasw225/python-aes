import python_aes.column_mixer
import python_aes.row_shifter
from python_aes.aes256 import add_roundkey
from python_aes.text_to_number_conversion import get_block_size_and_num_rows


def test_shift_blocks(random_test_block):
    block_size, num_rows = get_block_size_and_num_rows(random_test_block)
    shifted = python_aes.row_shifter.shift(
        random_test_block, num_rows=num_rows, block_size=block_size
    )
    assert (
        python_aes.row_shifter.shift(
            shifted, invert=True, num_rows=num_rows, block_size=block_size
        )
        == random_test_block
    )


def test_mix_columns(random_test_block):
    _, num_rows = get_block_size_and_num_rows(random_test_block)
    assert (
        python_aes.column_mixer.mix_invert(
            python_aes.column_mixer.mix(block=random_test_block, n=num_rows), n=num_rows
        )
        == random_test_block
    )


def test_add_roundkey(random_test_block, key):
    result = add_roundkey(random_test_block, key)
    assert add_roundkey(result, key) == random_test_block


def test_shift_known_vector():
    b = [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]
    original = list(b)
    shifted = python_aes.row_shifter.shift(b, num_rows=4, block_size=16)
    assert shifted == [
        0,
        85,
        170,
        255,
        68,
        153,
        238,
        51,
        136,
        221,
        34,
        119,
        204,
        17,
        102,
        187,
    ]
    restored = python_aes.row_shifter.shift(b, num_rows=4, block_size=16, invert=True)
    assert restored == original


def test_mix_known_vector():
    b = [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]
    assert python_aes.column_mixer.mix(b, n=4) == [
        34,
        119,
        0,
        85,
        102,
        51,
        68,
        17,
        170,
        255,
        136,
        221,
        238,
        187,
        204,
        153,
    ]
