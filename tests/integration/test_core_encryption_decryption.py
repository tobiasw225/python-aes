from python_aes.aes256 import AESBase
from python_aes.text_to_number_conversion import (
    ascii_file_to_blocks,
    string_to_blocks,
    utf_text_file_to_blocks,
)
from tests.utils_test import assert_blocks_equal


def test_ascii_string(default_hex_key, test_string):
    aes = AESBase(key=default_hex_key)
    blocks = string_to_blocks(test_string, block_size=aes.block_size)
    enc_blocks = [aes.encrypt_block(block) for block in blocks]
    dec_blocks = [aes.decrypt_block(block) for block in enc_blocks]
    assert_blocks_equal(dec_blocks, blocks)


def test_ascii_file(default_hex_key, small_txt_file_name):
    aes = AESBase(key=default_hex_key)
    blocks = ascii_file_to_blocks(filename=small_txt_file_name)
    enc_blocks = [aes.encrypt_block(block) for block in blocks]
    dec_blocks = [aes.decrypt_block(block) for block in enc_blocks]
    for a, b in zip(dec_blocks, blocks):
        assert a == b


def test_utf8_file(default_hex_key, original_hebrew_file_name):
    aes = AESBase(key=default_hex_key)
    original_blocks = list(utf_text_file_to_blocks(original_hebrew_file_name))
    enc_blocks = [aes.encrypt_block(block) for block in original_blocks]
    dec_blocks = [aes.decrypt_block(block) for block in enc_blocks]
    for a, b in zip(dec_blocks, original_blocks):
        assert a == b


def test_encrypt_block(default_hex_key, random_test_block):
    aes = AESBase(key=default_hex_key)
    enc_block = aes.encrypt_block(random_test_block)
    dec_block = aes.decrypt_block(enc_block)
    assert_blocks_equal(dec_block, random_test_block)
