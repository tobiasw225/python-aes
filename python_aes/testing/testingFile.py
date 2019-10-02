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
from python_aes.keyManager import *
from python_aes.AES256 import encrypt
from python_aes.AES256 import decrypt


mask = "<enctext>"


class AESInterface():
    def __init__(self):
        self.expanded_key = None
        self.key = None
        self.set_rand_key(key_name="/home/tobias/mygits/python-aes/keys/gKey")

        self.init_vector = [0] * 16
        for i in range(16):
            number = random.randint(0, 0xFF)
            self.init_vector[i] = number

    def set_rand_key(self, key_name="../keys/gKey"):
        """
        :param key_name
        :return:
        """
        self.key = get_key(key_name)
        self.expanded_key = expand_key(self.key)

    """
    encryption methods
    """
    def encrypt_blocks(self, filename=""):
        """
        :param filename:
        :param last_block:
        :return:
        """
        last_block = self.init_vector

        for block in blocks_of_file(filename):
            for i in range(16):
                block[i] ^= last_block[i]
            last_block = encrypt(block, self.expanded_key)
            yield last_block

    def encrypt_file(self, filename=""):
        """

        :param filename:
        :return:
        """
        if not filename:
            raise ValueError('no filename')
        fout_name = '../../res/enc'
        print('write to %s'% fout_name)
        block_ctr = 0
        buffer = ""

        for enc_block in self.encrypt_blocks(filename):
            buffer += "".join(str(format(sign, '02x')) for sign in enc_block)
            if block_ctr % 2:
                with open(file=fout_name, mode='at') as fout:
                    fout.write(buffer)
                    fout.write('\n')
                    buffer = ""
            block_ctr += 1

    """
    decryption methods
    """
    def decrypt_blocks(self, filename=""):
        """

        :param filename:
        :return:
        """
        last_block = self.init_vector

        for block in self.get_encrypted_blocks(filename):
            db = decrypt(block, self.expanded_key)
            for i in range(16):
                last_block[i] ^= db[i]

            last_block = block
            yield last_block

    def decrypt_file(self, filename=""):
        """

        :param filename:
        :return:
        """
        print("@todo implement. doesn't work yet")
        if not filename:
            raise ValueError('no filename')
        out_file = "../../res/dec"

        if os.path.isfile(out_file):
            os.remove(out_file)

        block_ctr = 0
        buffer = ""
        for block in self.decrypt_blocks(filename):
            pass
            # for i in range(16):
            #     try:
            #         buffer += chr(block[i])
            #     except:
            #         pass
            # if block_ctr % 2:
            #     with open(file=out_file, mode='at') as fout:
            #         fout.write(buffer)
            #         buffer = ""
            # block_ctr += 1

    def get_encrypted_blocks(self, filename=""):
        """
        :param filename:
        :param last_block
        :return:
        """
        with open(file=filename, mode='r') as fin:
            while fin:
                line = fin.readline()
                line_length = len(line)
                half_line = round(line_length/2)

                if line_length:
                    first_block = line[:half_line]
                    second_block = line[half_line:]

                    yield split_2_pairs(first_block)
                    yield split_2_pairs(second_block)


def split_2_pairs(enc_text_block=""):
    """

    :param enc_text_block:
    :return:
    """
    u = re.findall('..', enc_text_block)  # splits the string in 2pairs
    u = map(fmap, u)
    blocks = list(u)
    if len(blocks) % 16 == 0:
        while len(blocks) % 16 != 0:
            blocks.append(0)
    return blocks


def blocks_of_file(filename="", block_size=16):
    """

    :param block_size:
    :param filename:
    :return:
    """
    with open(file=filename, mode="rb") as f:
        eof = False
        ima = f.read(block_size)

        ima = binascii.hexlify(ima)
        block = [number for number in ima]

        if block:
            yield block

        while ima and not eof:
            ima = f.read(block_size)
            length_of_byte = len(ima)

            if length_of_byte == 0:
                continue

            if length_of_byte < block_size:
                for i in range(length_of_byte, block_size):
                    ima += b'0'  # verbesserungswuerdig
                eof = True  # when you have to fill up, it means you've reached eof
            ima = binascii.hexlify(ima)
            block = [number for number in ima]
            if block:
                yield block


#andere frage: wie schreibt man das dann wieder in die datei?
if __name__ == '__main__':
    my_aes  = AESInterface()
    #my_aes.encrypt_file(filename='../../res/tWotW.txt')
    my_aes.decrypt_file(filename="../../res/enc")
    print('finish?')


