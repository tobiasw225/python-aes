from __future__ import division , absolute_import
from __future__ import print_function, unicode_literals


from python_aes.aes256 import encrypt
from python_aes.aes256 import decrypt
from python_aes.helper import hex_string
from python_aes.read_block_file import get_blocks
from python_aes.helper import get_key
from python_aes.key_manager import *
from python_aes.text_encoding import *


def encrypt_file(key: list,
                 filename: str,
                 output_file: str,
                 encoding: str = 'utf-8'):
    blocks = []
    if encoding == 'utf-8':
        blocks = text_to_utf(encoding='utf-8', filename=filename)
    if encoding == 'ascii':
        blocks = text_file_to_blocks(filename)
    expanded_key = expand_key(key)
    with open(output_file, 'w') as fout:
        for block in blocks:
            fout.write(
                hex_string(
                    encrypt(block, expanded_key)
                ))


def decrypt_file(key: list,
                 filename: str,
                 encoding: str = 'utf-8') -> str:
    blocks = get_blocks(filename)
    expanded_key = expand_key(key)
    dec_blocks = [decrypt(block, expanded_key) for block in blocks]
    if encoding == 'ascii':
        return "".join(decode_blocks_to_string(dec_blocks))
    if encoding == 'utf-8':
        return "".join(utf_to_text(dec_blocks, enc=encoding))
    

if __name__ == '__main__':

    filename = "../res/test.txt"
    key = get_key("../keys/gKey")
    encrypt_file(key=key,
                 filename=filename,
                 output_file='../res/encrypted')
    print(decrypt_file(key=key, filename="../res/encrypted"))
