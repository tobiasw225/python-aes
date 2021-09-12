import random

import pytest
from implementation.aes_ctr_mode import StringCounterMode
from test.utils_test import sample_nonce


@pytest.mark.parametrize("block_size", [16, 32, 48, 56])
def test_set_nonce_length_positive(hex_key, block_size):
    my_aes = StringCounterMode(block_size=block_size)
    my_aes.set_key(hex_key)
    my_aes.set_nonce(sample_nonce(block_size // 2))


@pytest.mark.parametrize("block_size", [16, 32, 48, 56])
def test_set_nonce_length_negative(hex_key, block_size):
    my_aes = StringCounterMode(block_size=block_size)
    my_aes.set_key(hex_key)
    invalid_nonce = sample_nonce(block_size * random.randint(1, 100))
    with pytest.raises(ValueError):
        my_aes.set_nonce(invalid_nonce)
