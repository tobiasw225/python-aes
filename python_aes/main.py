from __future__ import division , absolute_import
from __future__ import print_function, unicode_literals


from python_aes.AES256 import encrypt
from python_aes.AES256 import decrypt

from python_aes.readBlockFile import get_blocks
from python_aes.helper import get_key
from python_aes.keyManager import *
from python_aes.text_encoding import *

"""
    Function to generate a random 32-Bit Key which is saved in gKey
"""


def block_to_text(block: list):
    """

    :param block:
    :return:
    """
    for sign in block:
        yield str(format(sign, '02x'))
    yield '\n'


def encrypt_text(text: str, key: list) -> list:
    """

    :param text:
    :return:
    """
    blocks = string_to_blocks(text)
    expanded_key = expand_key(key)
    enc_blocks = [encrypt(block, expanded_key) for block in blocks]
    return enc_blocks


def encrypt_file(key: list,
                 filename: str,
                 output_file: str,
                 enc: str = 'utf-8'):
    """

    :param key:
    :param filename:
    :param output_file:
    :param enc:
    :return:
    """
    blocks = []
    if enc == 'utf-8':
        blocks = text_to_utf(enc='utf-8', filename=filename)
    if enc == 'ascii':
        blocks = text_file_to_blocks(filename)

    expanded_key = expand_key(key)

    with open(output_file, 'w') as fout:
        for block in blocks:
            fout.write("".join(
                block_to_text(
                    encrypt(block, expanded_key)
                )))


def decrypt_file(key: list,
                 filename: str,
                 enc: str = 'utf-8'):
    """
    :param key:
    :param filename:
    :param enc:
    :return:
    """
    blocks = get_blocks(filename)
    expanded_key = expand_key(key)
    dec_blocks= [decrypt(block,expanded_key) for block in blocks]
    if enc == 'ascii':
        return "".join(decode_blocks_to_string(dec_blocks))
    if enc == 'utf-8':
        return "".join(utf_to_text(dec_blocks, enc=enc))
    

if __name__ == '__main__':

    filename = "../res/test.txt"
    key = get_key("../keys/gKey")
    encrypt_file(key=key, filename=filename, output_file='../res/encrypted')
    print(decrypt_file(key=key, filename="../res/encrypted"))