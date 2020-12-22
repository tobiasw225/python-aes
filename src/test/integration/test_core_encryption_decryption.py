from aes256 import decrypt, encrypt
from utils import string_to_blocks, utf_text_file_to_blocks, ascii_file_to_blocks
from test.utils_test import assert_blocks_equal


def test_ascii_string(expanded_key, test_string):
    blocks = string_to_blocks(test_string, block_size=16)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
    assert_blocks_equal(dec_blocks, blocks)


def test_ascii_file(expanded_key, original_txt_file):
    with original_txt_file as file:
        blocks = ascii_file_to_blocks(filename=file.name)
        enc_blocks = [encrypt(block, expanded_key) for block in blocks]
        dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
        for a, b in zip(dec_blocks, blocks):
            assert a == b


def test_utf8_file(expanded_key, original_hebrew_file):
    with original_hebrew_file as file:
        blocks = utf_text_file_to_blocks(file.name)
        enc_blocks = [encrypt(block, expanded_key) for block in blocks]
        dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
        blocks = utf_text_file_to_blocks(file.name)
        for a, b in zip(dec_blocks, blocks):
            assert a == b


def test_encrypt_block(expanded_key, random_test_block):
    enc_block = encrypt(random_test_block, expanded_key)
    dec_block = decrypt(enc_block, expanded_key)
    assert_blocks_equal(dec_block, random_test_block)