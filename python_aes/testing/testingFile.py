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

    def encrypt_file(self, filename: str) -> str:
        """
            encrypts file block by block
            and returns the encrypted byte-string.

        :param filename:
        :return:
        """
        assert os.path.isfile(filename)
        last_block = self.init_vector
        for block in blocks_of_file(filename):
            block = np.bitwise_xor(block, last_block)
            last_block = encrypt(block, self.expanded_key)
            yield "".join(str(format(sign, '02x'))
                          for sign in last_block)


    def decrypt_file(self, filename: str):
        """
             not working yet.

        :param filename:
        :return:
        """
        last_block = self.init_vector

        with open(file=filename, mode='r') as fin:
            while fin:
                line = fin.readline()
                block = process_block(line)
                if len(block) < 16:
                    _block = np.full(16, fill_value=0, dtype=int)
                    _block[:len(block)] = block
                    block = _block

                db = decrypt(block, self.expanded_key)
                last_block = np.bitwise_xor(last_block, db)
                yield decode_block(last_block)


def blocks_of_file(filename: str, block_size: int = 8):
    """

    :param block_size:
    :param filename:
    :return:
    """
    assert os.path.isfile(filename)

    with open(file=filename, mode="rb") as fin:
        eof = False
        content = fin.read(block_size)

        block = [number for number in binascii.hexlify(content)]

        if block:
            yield block

        while content and not eof:
            content = fin.read(block_size)
            len_byte = len(content)

            if not len_byte:
                continue

            if len_byte < block_size:
                content += b'0'*(block_size-len_byte)
                # when you have to fill up, it means you've reached eof
                eof = True
            block = [number for number in binascii.hexlify(content)]
            if block:
                yield block


if __name__ == '__main__':
    my_aes = AESInterface()
    # with open("../../res/enc", 'w') as fout:
    #     for enc_block in my_aes.encrypt_file(filename='../../res/tWotW.txt'):
    #         print(enc_block)
    #         fout.write(enc_block + "\n")
    for block in my_aes.decrypt_file(filename="../../res/enc"):
        print(block)
    # print('finish?')


