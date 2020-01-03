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

import numpy as np

from python_aes.helper import get_key
from python_aes.helper import process_block
from python_aes.keyManager import *
from python_aes.AES256 import encrypt
from python_aes.AES256 import decrypt
from python_aes.text_encoding import decode_block
from python_aes.process_byte_files import block_to_byte
from python_aes.process_byte_files import blocks_of_file

mask = "<enctext>"


class AESInterface(object):

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

    def encrypt_file(self, filename: str, output_file: str):
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
                # cbc (comment out for ecb)
                block = np.bitwise_xor(block, last_block)
                last_block = encrypt(block, self.expanded_key)
                fout.write(block_to_byte(last_block))


    def decrypt_file(self, filename: str, output_file: str):
        """

        :param filename:
        :param output_file:
        :return:
        """
        last_block = self.init_vector
        with open(output_file, 'wb') as fout:
            _buffer = None
            for block in blocks_of_file(filename):
                dec_block = decrypt(block, self.expanded_key)
                # cbc (comment out for ecb)
                dec_block = np.bitwise_xor(last_block, dec_block)

                if _buffer is not None:
                    fout.write(block_to_byte(_buffer))
                _buffer = dec_block
                last_block = block

            # last block: remove all dangling elements.
            _buffer = np.array(list(filter(lambda x: x != 0, _buffer)))
            fout.write(block_to_byte(_buffer))


if __name__ == '__main__':
    my_aes = AESInterface()
    print(my_aes.init_vector)

    filename = "/home/tobias/Schreibtisch/insert_protokoll{}.txt"
    filename = "/home/tobias/Bilder/mail-logo{}.jpg"
    output_file = filename.format('.enc')
    print(output_file)
    my_aes.encrypt_file(filename=filename.format(''),
                        output_file=output_file)
    dec_file = filename.format('.dec')
    print(my_aes.init_vector, dec_file)
    my_aes.decrypt_file(filename=output_file,
                        output_file=dec_file)