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
from itertools import cycle
from typing import List

from helper import hex_string, generate_nonce
from python_aes.helper import get_key
from python_aes.key_manager import *
from python_aes.aes256 import encrypt
from python_aes.aes256 import decrypt
from python_aes.text_encoding import string_to_blocks
from python_aes.text_encoding import chr_decode
from python_aes.helper import process_block
from python_aes.helper import chunks

from python_aes.process_bytes import block_to_byte
from python_aes.process_bytes import blocks_of_file
from python_aes.process_bytes import blocks_of_string


class AESInterface(ABC):
    """
        Interface for AES implementations Text & Byte

    """

    def __init__(self):
        self.expanded_key = None
        self.key = None
        self.set_key(key="/home/tobias/mygits/python-aes/keys/gKey")
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

    def set_key(self, key: str = "../keys/gKey"):
        """
            The key can be either a file (plain-text hex-digits)
            or passed as string.

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
            yield hex_string(last_block)

    def decrypt(self, text: str) -> str:
        """
        :param text: encrypted
        :return:
        """
        last_block = self.init_vector
        blocks = process_block(text)
        for block in chunks(blocks):
            dec_block = decrypt(block, self.expanded_key)
            last_block = np.bitwise_xor(last_block, dec_block)
            yield "".join([chr_decode(c) for c in last_block])
            last_block = block


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


class AESStringCTR(AESInterface):
    """

    """
    def __init__(self, block_size: int = 16):
        super().__init__()
        self.ctr = 0
        # first half is for nonce, rest is for counter
        self.block_size = block_size
        assert block_size == 16
        # dummy nonce for testing.
        self._nonce = np.zeros(block_size, dtype=int)
        self._nonce[:block_size//2] = generate_nonce(d_type='int',
                                                     block_size=block_size // 2)

    def nonce(self, i):
        ctr = str(i).zfill(self.block_size//2)
        _nonce = self._nonce
        _nonce[self.block_size//2:] = [ord(i) for i in ctr]
        return _nonce

    def set_nonce(self, nonce: str):
        """

        :param nonce:
        :return:
        """
        nonce = process_block(nonce)
        assert len(nonce)*2 == self.block_size
        self._nonce = np.zeros(self.block_size, dtype=int)
        self._nonce[:self.block_size // 2] = nonce

    def encrypt(self, text: str) -> str:
        """
        :param text:
        :return:
        """
        blocks = blocks_of_string(text, block_size=self.block_size)
        for i, block in enumerate(blocks):
            enc_nonce = encrypt(self.nonce(i), self.expanded_key)
            enc_nonce = hex_string(enc_nonce)
            enc_block = [a ^ b for (a, b) in zip(bytes(block, 'utf-8'),
                                                 cycle(bytes(enc_nonce, 'utf-8')))]
            yield block_to_byte(enc_block)

    def decrypt(self, text_blocks: List[str]) -> str:
        """
        :param text_blocks: encrypted
        :return:
        """
        # b''.join(b)
        # slicing possible
        for i, block in enumerate(text_blocks):
            dec_nonce = encrypt(my_aes.nonce(i), my_aes.expanded_key)
            dec_nonce = hex_string(dec_nonce)
            dec_text = [a ^ b for (a, b) in zip(bytes(block),
                                                cycle(bytes(dec_nonce, 'utf-8')))]
            # remove dangling elements.
            if 0 in dec_text:
                dec_text = list(filter(None, dec_text))
            yield bytes(dec_text).decode()


if __name__ == '__main__':
    my_aes = AESStringCTR(block_size=16)
    my_aes.set_key('8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1')
    my_aes.init_vector = '7950b9c141ad3d6805dea8585bc71b4b'
    my_aes.set_nonce('b2e47dd87113a99201a54904c61f7a6f51d1f92187294faf3b5d8e8dd07ce48b'[:16])

    test_string = "123456sehr gut. ich bin dann doch etwas müde heute abend und sumpfe hier nur rum ;)"

    enc = list(my_aes.encrypt(test_string))

    # print(enc)
    dec = "".join(s for s in my_aes.decrypt(enc))
    print('decrypted')
    print(dec)
    print()
    print('congrats!' if dec == test_string else 'pitty...')
    # print(test_string)

    ###

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
