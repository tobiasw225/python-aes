import tempfile

from itertools import cycle
import filecmp

from src.helper import hex_string
from src.test.utils import sample_nonce
from src.aes256 import encrypt
from src.aes_ctr_mode import AESStringCTR, AESBytesCTR
from src.util import text_blocks


def test_xor(test_string):
    my_aes = AESStringCTR()
    my_aes.set_nonce(sample_nonce(8))
    nonce = my_aes.nonce(0)
    nonce = hex_string(nonce)
    enc_text = [
        a ^ b
        for (a, b) in zip(bytes(test_string, "utf-8"), cycle(bytes(nonce, "utf-8")))
    ]
    dec_text = [a ^ b for (a, b) in zip(bytes(enc_text), cycle(bytes(nonce, "utf-8")))]
    assert test_string == bytes(dec_text).decode()


def test_enc_dec_step(test_string, hex_key):
    my_aes = AESStringCTR()
    my_aes.set_key(hex_key)
    my_aes.set_nonce(sample_nonce(8))
    enc_nonce = encrypt(my_aes.nonce(0), my_aes.expanded_key)
    enc_nonce = hex_string(enc_nonce)
    enc_block = [
        a ^ b
        for (a, b) in zip(bytes(test_string, "utf-8"), cycle(bytes(enc_nonce, "utf-8")))
    ]
    dec_nonce = encrypt(my_aes.nonce(0), my_aes.expanded_key)
    dec_nonce = hex_string(dec_nonce)
    assert enc_nonce == dec_nonce
    dec_text = [
        a ^ b for (a, b) in zip(bytes(enc_block), cycle(bytes(enc_nonce, "utf-8")))
    ]
    assert test_string == bytes(dec_text).decode()


def test_enc_dec_full(random_wiki_articles, hex_key):
    my_aes = AESStringCTR()
    my_aes.set_key(hex_key)
    my_aes.set_nonce(sample_nonce(8))
    blocks = text_blocks(random_wiki_articles, block_size=16)
    for i, block in enumerate(blocks):
        enc_nonce = encrypt(my_aes.nonce(i), my_aes.expanded_key)
        enc_nonce = hex_string(enc_nonce)
        enc_block = [
            a ^ b
            for (a, b) in zip(bytes(block, "utf-8"), cycle(bytes(enc_nonce, "utf-8")))
        ]
        dec_nonce = encrypt(my_aes.nonce(i), my_aes.expanded_key)
        dec_nonce = hex_string(dec_nonce)
        assert enc_nonce == dec_nonce
        dec_text = [
            a ^ b for (a, b) in zip(bytes(enc_block), cycle(bytes(enc_nonce, "utf-8")))
        ]
        assert block == bytes(dec_text).decode()


def test_bytes_full(original_byte_file, hex_key):
    my_aes = AESBytesCTR()
    my_aes.set_key(hex_key)
    my_aes.set_nonce(sample_nonce(8))
    with original_byte_file as in_file, tempfile.NamedTemporaryFile() as enc_file, tempfile.NamedTemporaryFile() as dec_file:
        my_aes.encrypt(filename=in_file.name, output_file=enc_file.name)
        my_aes.decrypt(filename=enc_file.name, output_file=dec_file.name)
        assert filecmp.cmp(in_file.name, dec_file.name) is True
