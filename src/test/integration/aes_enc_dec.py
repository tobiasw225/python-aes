import numpy as np

from src.aes256 import encrypt
from src.aes256 import decrypt


def test_encrypt_block(expanded_key, random_test_block):
    enc_block = encrypt(random_test_block, expanded_key)
    dec_block = decrypt(enc_block, expanded_key)
    assert np.allclose(dec_block, random_test_block) is True
