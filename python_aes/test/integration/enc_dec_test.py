import os

import numpy as np
from python_aes.aes256 import decrypt
from python_aes.aes256 import encrypt
from python_aes.key_manager import expand_key
from python_aes.text_util import string_to_blocks, text_file_to_blocks
from python_aes.text_util import ascii_file_to_blocks


def test_ascii_string(key, test_string):
    blocks = string_to_blocks(test_string, block_size=16)
    expanded_key = expand_key(key)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, blocks) is True


def test_ascii_file(key, original_txt_file):
    blocks = ascii_file_to_blocks(filename=original_txt_file)
    expanded_key = expand_key(key)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, blocks) is True


def test_utf8_file(key, original_hebrew_file):
    # list to compare afterwards @todo reset generator?
    blocks = list(text_file_to_blocks(original_hebrew_file))
    expanded_key = expand_key(key)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, np.array(list(blocks))) is True
    os.remove(original_hebrew_file)