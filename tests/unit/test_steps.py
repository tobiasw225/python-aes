from base.steps import BlockShifter, ColumnMixer, add_roundkey
from base.text_to_number_conversion import get_block_size_and_num_rows


def test_shift_blocks(random_test_block):
    block_size, num_rows = get_block_size_and_num_rows(random_test_block)
    bs = BlockShifter(num_rows=num_rows, block_size=block_size)
    shifted = bs.shift(random_test_block)
    assert bs.shift(shifted, invert=True) == random_test_block


def test_mix_columns(random_test_block):
    block_size, num_rows = get_block_size_and_num_rows(random_test_block)
    cm = ColumnMixer(num_rows=num_rows, block_size=block_size)
    assert cm.mix_invert(cm.mix(random_test_block)) == random_test_block


def test_add_roundkey(random_test_block, key):
    assert add_roundkey(random_test_block, key) == add_roundkey(key, random_test_block)
