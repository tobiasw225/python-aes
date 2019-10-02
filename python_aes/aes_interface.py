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

import numpy as np

from python_aes.helper import get_key
from python_aes.keyManager import *
from python_aes.AES256 import encrypt
from python_aes.AES256 import decrypt
from python_aes.text_encoding import string_to_blocks
from python_aes.text_encoding import decode_blocks_to_string
from python_aes.helper import process_block
from python_aes.helper import chunks


mask = "<enctext>"


class AESInterface():
    """
        Uses CBC

    """

    def __init__(self):
        self.expanded_key = None
        self.key = None
        self.set_rand_key(key_name="/home/tobias/mygits/python-aes/keys/gKey")
        self.init_vector = np.random.randint(0, 255, 16)

    def set_rand_key(self, key_name: str = "../keys/gKey"):
        """
              not sure if that's safe, but it's faster.
              (it's only for fun so far ;) )

        :param key_name
        :return:
        """
        self.key = get_key(key_name)
        self.expanded_key = expand_key(self.key)

    def encrypt_string(self, text: str) -> str:
        """
        @todo generator
        :param text:
        :return:
        """
        last_block = self.init_vector
        blocks = string_to_blocks(mask + text + mask)
        enc_block = []
        for block in blocks:
            block = [block[i] ^ last_block[i] for i in range(16)]
            last_block = encrypt(block, self.expanded_key)
            enc_block.append(last_block)
        return "".join(["".join([str(format(sign, '02x')) for sign in block]) for block in enc_block])

    def decrypt_string(self, text: str) -> str:
        """
        @todo generator
        :param text: encrypted
        :return:
        """
        last_block = self.init_vector

        blocks = process_block(text)
        # if the block is less than 16 signs long append 0s
        if len(blocks) % 16 == 0:
            while len(blocks) % 16 != 0:
                blocks.append(0)
        dec_blocks = []

        for block in chunks(blocks):
            # i want to have nice chunks of 16 numbers
            dec_block = decrypt(block, self.expanded_key)
            last_block = [lb ^ db for lb, db in zip(last_block, dec_block)]
            dec_blocks.append(last_block)
            last_block = block
        # text is masked => extract only text
        return "".join(decode_blocks_to_string(blocks=dec_blocks)).split(mask)[1]


if __name__ == '__main__':
    my_aes = AESInterface()

    enc = my_aes.encrypt_string("sehr gut.")
    print(enc)
    print(my_aes.decrypt_string(enc))
