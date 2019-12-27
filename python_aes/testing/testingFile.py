#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: aes_inteface.py
#
# __description__: use this class to encrypt/ decrypt strings with aes256
#
# __remark__:
#
# __todos__: randkey
#
# Created by Tobias Wenzel in December 2017
# Copyright (c) 2017 Tobias Wenzel

from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals
from sys import maxsize

import binascii
import os

from python_aes.helper import get_key
from python_aes.helper import process_block
from python_aes.keyManager import *
from python_aes.AES256 import encrypt
from python_aes.AES256 import decrypt
from python_aes.text_encoding import decode_block

mask = "<enctext>"


class AESInterface():
    def __init__(self):
        self.expanded_key = None
        self.key = None
        self.set_rand_key(key_name="/home/tobias/mygits/python-aes/keys/gKey")
        self.init_vector = np.random.randint(0, 255, 16)

    def set_rand_key(self, key_name="../keys/gKey"):
        """
        :param key_name
        :return:
        """
        self.key = get_key(key_name)
        self.expanded_key = expand_key(self.key)

    def encrypt_file(self, filename: str, output_file: str) -> str:
        """
            encrypts file block by block
            and returns the encrypted byte-string.

        :param filename:
        :return:
        """
        assert os.path.isfile(filename)
        last_block = self.init_vector
        with open(output_file, 'wb') as fout:
            for block in blocks_of_file(filename):
                # block = np.bitwise_xor(block, last_block)
                # last_block = encrypt(block, self.expanded_key)
                fout.write(block_to_byte(encrypt(block, self.expanded_key)))

    def decrypt_file(self, filename: str, output_file: str):
        """

        :param filename:
        :param output_file:
        :return:
        """
        last_block = self.init_vector
        with open(output_file, 'wb') as fout:

            dec_block = [0]*len(last_block)
            for block in blocks_of_file(filename):
                # cbc

                # dec_block = decrypt(block, self.expanded_key)
                # last_block = np.bitwise_xor(last_block, dec_block)

                # ecb -> plain stupid, but it works ;)
                # @todo last block is still dangling.
                dec_block = block_to_byte(decrypt(block, self.expanded_key))
                fout.write(dec_block)


def blocks_of_file(filename: str, block_size: int = 16):
    """

    :param block_size:
    :param filename:
    :return:
    """
    assert os.path.isfile(filename)
    with open(file=filename, mode="rb") as fin:
        eof = False
        content = fin.read(block_size)

        if content:
            yield np.array([number for number in content])
        while content and not eof:
            content = fin.read(block_size)
            len_byte = len(content)

            if not len_byte:
                continue

            if len_byte < block_size:
                content = [number for number in content]
                content.extend([0]*(block_size-len_byte))
                # when you have to fill up, it means you've reached eof
                eof = True
            if content:
                yield np.array([number for number in content])


def block_to_byte(block: np.ndarray) -> bytes:
    """

    :param block:
    :return:
    """
    b_block = [hex(number)[2:].zfill(2) for number in block]
    return binascii.unhexlify("".join(b_block))


if __name__ == '__main__':
    my_aes = AESInterface()
    # this seems to be working.
    print(my_aes.init_vector)
    filename = "/home/tobias/Schreibtisch/insert_protokoll.txt"
    output_file = filename+'.enc'
    print(output_file)
    my_aes.encrypt_file(filename=filename,
                        output_file=output_file)
    # decryption +- working, but can't read file.
    dec_file = filename+'.dec'
    # print(my_aes.init_vector, dec_file)
    my_aes.decrypt_file(filename=output_file,
                        output_file=dec_file)

# block = [number for number in binascii.hexlify(content)]
# print([number for number in content])
# # conversion of bytes to ascii (hex-utf-8-) string
# dec = binascii.hexlify(content).decode('utf-8')
# print(dec)
# # conversion of numbers (which i will get back from the
# # encryption) to bytes
# print([hex(number) for number in content])
# # this enables me to write data back into the file
# print(binascii.unhexlify(dec))
