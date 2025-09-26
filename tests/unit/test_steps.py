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
    assert add_roundkey(random_test_block, key) == add_roundkey(key, random_test_block)
