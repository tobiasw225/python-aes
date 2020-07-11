from itertools import cycle
import filecmp

from python_aes.helper import hex_string
from python_aes.aes256 import encrypt
from python_aes.aes_interface import AESStringCTR, AESBytesCTR
from python_aes.text_encoding import text_blocks


def test_xor(test_string):
    my_aes = AESStringCTR()
    nonce = my_aes.nonce(0)
    nonce = hex_string(nonce)
    enc_text = [
        a ^ b
        for (a, b) in zip(bytes(test_string, "utf-8"),
                          cycle(bytes(nonce, "utf-8")))
    ]
    dec_text = [a ^ b for (a, b) in zip(bytes(enc_text),
                                        cycle(bytes(nonce, "utf-8")))]
    assert test_string == bytes(dec_text).decode()


def test_enc_dec_step(test_string):
    my_aes = AESStringCTR()
    enc_nonce = encrypt(my_aes.nonce(0), my_aes.expanded_key)
    enc_nonce = hex_string(enc_nonce)
    enc_block = [
        a ^ b
        for (a, b) in zip(bytes(test_string, "utf-8"),
                          cycle(bytes(enc_nonce, "utf-8")))
    ]
    dec_nonce = encrypt(my_aes.nonce(0), my_aes.expanded_key)
    dec_nonce = hex_string(dec_nonce)
    assert enc_nonce == dec_nonce
    dec_text = [
        a ^ b for (a, b) in zip(bytes(enc_block),
                                cycle(bytes(enc_nonce, "utf-8")))
    ]
    assert test_string == bytes(dec_text).decode()


def test_enc_dec_full(random_wiki_articles):
    my_aes = AESStringCTR()
    # my_aes.set_nonce(sample_nonce(16))
    blocks = text_blocks(random_wiki_articles, block_size=16)
    for i, block in enumerate(blocks):
        enc_nonce = encrypt(my_aes.nonce(i), my_aes.expanded_key)
        enc_nonce = hex_string(enc_nonce)
        enc_block = [
            a ^ b
            for (a, b) in zip(bytes(block, "utf-8"),
                              cycle(bytes(enc_nonce, "utf-8")))
        ]
        dec_nonce = encrypt(my_aes.nonce(i), my_aes.expanded_key)
        dec_nonce = hex_string(dec_nonce)
        assert enc_nonce == dec_nonce
        dec_text = [
            a ^ b for (a, b) in zip(bytes(enc_block),
                                    cycle(bytes(enc_nonce, "utf-8")))
        ]
        assert block == bytes(dec_text).decode()


def test_bytes_full(original_byte_file,
                    dec_byte_file,
                    enc_byte_file):
    my_aes = AESBytesCTR()
    my_aes.encrypt(filename=original_byte_file, output_file=enc_byte_file)
    my_aes.decrypt(filename=enc_byte_file, output_file=dec_byte_file)
    assert filecmp.cmp(original_byte_file, dec_byte_file) is True
