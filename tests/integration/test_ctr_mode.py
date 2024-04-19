import filecmp
import tempfile
from itertools import cycle

import pytest

from python_aes.text_to_number_conversion import hex_string, text_blocks
from python_aes.aes_ctr_mode import ByteCounterMode, StringCounterMode
from tests.utils_test import sample_nonce


@pytest.mark.parametrize("block_size", [16, 32, 48, 56])
def test_xor(test_string, block_size):
    my_aes = StringCounterMode(block_size=block_size)
    my_aes.set_nonce(sample_nonce(block_size // 2))
    nonce = my_aes.nonce(0)
    nonce = hex_string(nonce)
    enc_text = [
        a ^ b
        for (a, b) in zip(bytes(test_string, "utf-8"), cycle(bytes(nonce, "utf-8")))
    ]
    dec_text = [a ^ b for (a, b) in zip(bytes(enc_text), cycle(bytes(nonce, "utf-8")))]
    assert test_string == bytes(dec_text).decode()


@pytest.mark.parametrize("block_size", [16, 32, 48, 56])
def test_enc_dec_step(test_string, hex_key, block_size):
    if block_size != 16:
        pytest.skip(f"Blocksize != 16 is not supported ({block_size})")
    my_aes = StringCounterMode(block_size=block_size)
    my_aes.set_key(hex_key(block_size))
    my_aes.set_nonce(sample_nonce(block_size // 2))
    enc_nonce = my_aes.encrypt_block(my_aes.nonce(0), my_aes.expanded_key)
    enc_nonce = hex_string(enc_nonce)
    enc_block = [
        a ^ b
        for (a, b) in zip(bytes(test_string, "utf-8"), cycle(bytes(enc_nonce, "utf-8")))
    ]
    dec_nonce = my_aes.encrypt_block(my_aes.nonce(0), my_aes.expanded_key)
    dec_nonce = hex_string(dec_nonce)
    assert enc_nonce == dec_nonce
    dec_text = [
        a ^ b for (a, b) in zip(bytes(enc_block), cycle(bytes(enc_nonce, "utf-8")))
    ]
    assert test_string == bytes(dec_text).decode()


def test_enc_dec_full(random_wiki_articles, hex_key):
    my_aes = StringCounterMode()
    my_aes.set_key(hex_key(16))
    my_aes.set_nonce(sample_nonce(8))
    blocks = text_blocks(random_wiki_articles, block_size=16)
    for i, block in enumerate(blocks):
        enc_nonce = my_aes.encrypt_block(my_aes.nonce(i), my_aes.expanded_key)
        enc_nonce = hex_string(enc_nonce)
        enc_block = [
            a ^ b
            for (a, b) in zip(bytes(block, "utf-8"), cycle(bytes(enc_nonce, "utf-8")))
        ]
        dec_nonce = my_aes.encrypt_block(my_aes.nonce(i), my_aes.expanded_key)
        dec_nonce = hex_string(dec_nonce)
        assert enc_nonce == dec_nonce
        dec_text = [
            a ^ b for (a, b) in zip(bytes(enc_block), cycle(bytes(enc_nonce, "utf-8")))
        ]
        assert block == bytes(dec_text).decode()


def test_ctr_mode_bytes_complete(original_byte_file, hex_key):
    my_aes = ByteCounterMode()
    my_aes.set_key(hex_key(16))
    my_aes.set_nonce(sample_nonce(8))
    with original_byte_file as in_file, tempfile.NamedTemporaryFile() as enc_file, tempfile.NamedTemporaryFile() as dec_file:
        my_aes.encrypt(filename=in_file.name, output_file=enc_file.name)
        my_aes.decrypt(filename=enc_file.name, output_file=dec_file.name)
        assert filecmp.cmp(in_file.name, dec_file.name) is True


@pytest.mark.parametrize("block_size", [16, 32, 48, 56])
def test_ctr_mode_string_complete(test_string, hex_key, block_size):
    if block_size != 16:
        pytest.skip(f"Blocksize != 16 is not supported ({block_size})")
    my_aes = StringCounterMode(block_size=block_size)
    my_aes.set_key(hex_key(block_size))
    my_aes.set_nonce(sample_nonce(block_size // 2))
    enc_text_blocks = list(my_aes.encrypt(test_string))
    dec_test = "".join([d for d in my_aes.decrypt(enc_text_blocks)])
    assert dec_test.strip() == test_string.strip()
