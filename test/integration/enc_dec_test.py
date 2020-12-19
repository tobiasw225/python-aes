import numpy as np
from src.aes256 import decrypt
from src.aes256 import encrypt
from src.key_manager import expand_key
from src.util import string_to_blocks, text_file_to_blocks
from src.util import ascii_file_to_blocks


def test_ascii_string(key, test_string):
    blocks = string_to_blocks(test_string, block_size=16)
    expanded_key = expand_key(key)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, blocks) is True


def test_ascii_file(key, original_txt_file):
    with original_txt_file as file:
        blocks = ascii_file_to_blocks(filename=file.name)
    expanded_key = expand_key(key)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, blocks) is True


def test_utf8_file(key, original_hebrew_file):
    # list to compare afterwards @todo reset generator?
    with original_hebrew_file as file:
        blocks = list(text_file_to_blocks(file.name))
    expanded_key = expand_key(key)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, np.array(list(blocks))) is True
