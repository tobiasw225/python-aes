from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from python_aes.aes256 import decrypt, encrypt
from python_aes.helper import get_key, hex_string
from python_aes.key_manager import expand_key
from python_aes.read_block_file import get_blocks
from python_aes.text_encoding import blocks_to_string
from python_aes.text_encoding import text_file_to_blocks


def encrypt_file(key: list, filename: str, output_file: str, encoding: str = "utf-8"):
    blocks = text_file_to_blocks(encoding=encoding, filename=filename)
    expanded_key = expand_key(key)
    with open(output_file, "w") as fout:
        for block in blocks:
            fout.write(hex_string(encrypt(block, expanded_key)))


def decrypt_file(key: list, filename: str, encoding: str = "utf-8") -> str:
    blocks = get_blocks(filename)
    expanded_key = expand_key(key)
    dec_blocks = [decrypt(block, expanded_key) for block in blocks]
    return blocks_to_string(dec_blocks, encoding)


if __name__ == "__main__":

    filename = "../res/test.txt"
    key = get_key("../keys/gKey")
    # todo fix
    encrypt_file(
        key=key, filename=filename,
        output_file="../res/encrypted",
        encoding="ascii"
    )
    for line in decrypt_file(key=key,
                             filename="../res/encrypted",
                             encoding="ascii"):
        print(line)
