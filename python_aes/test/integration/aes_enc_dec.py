import numpy as np

from python_aes.aes256 import encrypt
from python_aes.aes256 import decrypt


def test_encrypt_block(key, random_test_block):
    enc_block = encrypt(random_test_block, key)
    dec_block = decrypt(enc_block, key)
    assert np.allclose(dec_block, random_test_block) is True
