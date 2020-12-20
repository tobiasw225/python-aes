import numpy as np
from src.aes256 import decrypt
from src.aes256 import encrypt
from src.key_manager import expand_key
from src.util import string_to_blocks, utf_text_file_to_blocks
from src.util import ascii_file_to_blocks


def test_ascii_string(expanded_key, test_string):
    blocks = string_to_blocks(test_string, block_size=16)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, blocks) is True


def test_ascii_file(expanded_key, original_txt_file):
    with original_txt_file as file:
        blocks = ascii_file_to_blocks(filename=file.name)
        enc_blocks = [encrypt(block, expanded_key) for block in blocks]
        dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
        assert np.allclose(dec_blocks, blocks) is True


def test_utf8_file(expanded_key, original_hebrew_file):
    with original_hebrew_file as file:
        blocks = utf_text_file_to_blocks(file.name)
        enc_blocks = [encrypt(block, expanded_key) for block in blocks]
        dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
        blocks = utf_text_file_to_blocks(file.name)
        assert np.allclose(dec_blocks, np.array(list(blocks))) is True
