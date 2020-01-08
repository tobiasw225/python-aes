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
import os
from abc import abstractmethod
from abc import ABC

from python_aes.helper import get_key
from python_aes.keyManager import *
from python_aes.AES256 import encrypt
from python_aes.AES256 import decrypt
from python_aes.text_encoding import string_to_blocks
from python_aes.text_encoding import decode_blocks_to_string
from python_aes.helper import process_block
from python_aes.helper import chunks

from python_aes.process_byte_files import block_to_byte
from python_aes.process_byte_files import blocks_of_file

mask = "<enctext>"


class AESInterface(ABC):
    """
        Interface for AES implementations Text & Byte

    """

    def __init__(self):
        self.expanded_key = None
        self.key = None
        self.init_rand_key(key="/home/tobias/mygits/python-aes/keys/gKey")
        self._init_vector = np.random.randint(0, 255, 16)

    @property
    def init_vector(self):
        return self._init_vector

    @init_vector.setter
    def init_vector(self, key: str):
        """

        :param key:
        :return:
        """
        self._init_vector = get_key(key)

    def init_rand_key(self, key: str = "../keys/gKey"):
        """
           default key: not sure if that's safe, but it's faster.
              (it's only for fun so far ;) )

        :param key
        :return:
        """
        self.key = get_key(key)
        self.expanded_key = expand_key(self.key)

    @abstractmethod
    def encrypt(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        pass

    @abstractmethod
    def decrypt(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        pass


class AESString(AESInterface):
    """

    """
    def __init__(self):
        super().__init__()

    def encrypt(self, text: str) -> str:
        """
        :param text:
        :return:
        """
        last_block = self.init_vector
        blocks = string_to_blocks(text)
        for block in blocks:
            block = np.bitwise_xor(block, last_block)
            last_block = encrypt(block, self.expanded_key)
            yield "".join([str(format(sign, '02x')) for sign in last_block])

    def decrypt(self, text: str) -> str:
        """
        :param text: encrypted
        :return:
        """
        last_block = self.init_vector
        blocks = process_block(text)
        # if the block is less than 16 signs long append 0s
        # wird nicht benötigt!
        # if len(blocks) % 16 == 0:
        #     # when you have to fill up, it means you've reached eof
        #     print( len(blocks) )
        #     while len(blocks) % 16 != 0:
        #         blocks.append(0)
        dec_blocks = []

        for block in chunks(blocks):
            # i want to have nice chunks of 16 numbers
            dec_block = decrypt(block, self.expanded_key)
            last_block = np.bitwise_xor(last_block, dec_block)
            dec_blocks.append(last_block)
            last_block = block
        # text is masked => extract only text
        return "".join(decode_blocks_to_string(blocks=dec_blocks))


class AESBytes(AESInterface):

    def encrypt(self, filename: str, output_file: str):
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

    def decrypt(self, filename: str, output_file: str):
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
    my_aes = AESString()
    my_aes.init_rand_key('8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1')
    my_aes.init_vector = '7950b9c141ad3d6805dea8585bc71b4b'

    enc = ''
    for _enc in my_aes.encrypt("123456sehr gut. ich bin dann doch etwas müde heute abend und sumpfe hier nur rum ;)"):
        print(_enc)
        enc += _enc

    # enc = my_aes.encrypt("sehr gut.")
    print(enc)
    print(my_aes.decrypt(enc))
    #
    # my_aes = AESBytes()
    # print(my_aes.init_vector)
    #
    #
    # filename = "/home/tobias/Schreibtisch/insert_protokoll{}.txt"
    # filename = "/home/tobias/Bilder/sample/Hummingbird{}.jpg"
    # output_file = filename.format('.enc')
    # print(output_file)
    #
    # start = time()
    # my_aes.encrypt(filename=filename.format(''),
    #                     output_file=output_file)
    # print(time() - start)
    # dec_file = filename.format('.dec')
    # print(my_aes.init_vector, dec_file)
    # start = time()
    # my_aes.decrypt(filename=output_file,
    #                output_file=dec_file)
    # print(time() - start)


    # import argparse
    #
    # parser = argparse.ArgumentParser()
    #
    # parser.add_argument("--init_vector", help="Filename of zip-archive.")
    # parser.add_argument("--key", help="Key")
    # args = parser.parse_args()
    #
    # init_vector = args.init_vector
    # rand_key = args.key
    #
    #
    # my_aes = AESString()
    # my_aes.init_rand_key(rand_key)
    # my_aes.init_vector = init_vector
    # #
    # enc = my_aes.encrypt("sehr gut.")
    # print(enc)
    # print(my_aes.decrypt(enc))