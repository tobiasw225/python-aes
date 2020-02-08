from python_aes.aes256 import decrypt
from python_aes.aes256 import encrypt
from python_aes.key_manager import *
from python_aes.text_encoding import *


def test_ascii_string(key, test_string):
    blocks = string_to_blocks(test_string)
    expanded_key = expand_key(key)

    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, blocks) is True


def test_ascii_file(key, original_txt_file):
    blocks = text_file_to_blocks(filename=original_txt_file)
    expanded_key = expand_key(key)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, blocks) is True


def test_utf8_file(key, original_txt_file):
    blocks = text_to_utf(enc="utf-8", filename=original_txt_file)
    expanded_key = expand_key(key)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert np.allclose(dec_blocks, blocks) is True

