from steps import shift_block, mix_columns_inv, mix_columns, add_roundkey


def test_shift_blocks(random_test_block):
    shifted = shift_block(random_test_block)
    assert shift_block(shifted, invert=True) == random_test_block


def test_mix_columns(random_test_block):
    assert mix_columns_inv(mix_columns(random_test_block)) == random_test_block


def test_add_roundkey(random_test_block, key):
    assert add_roundkey(random_test_block, key) == add_roundkey(key, random_test_block)