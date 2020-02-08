import numpy as np

from python_aes.aes256 import encrypt
from python_aes.aes256 import decrypt


def test_aes(key, test_block):
    # Test with simple predefined block.
    enc_block = encrypt(test_block, key)
    dec_block = decrypt(enc_block, key)
    assert np.allclose(dec_block, test_block) is True

