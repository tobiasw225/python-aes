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
from python_aes.text_encoding import text_blocks
from python_aes.text_encoding import chr_decode
from python_aes.helper import process_block
from python_aes.helper import chunks

from python_aes.process_byte_files import block_to_byte
from python_aes.process_byte_files import blocks_of_file


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

from itertools import cycle


def xor(data, key):
    # return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(data, cycle(key)))
    return [a ^ b for (a, b) in zip(bytes(data, 'utf-8'), cycle(bytes(key, 'utf-8')))]

def hex_string(block):
    return "".join(str(format(sign, '02x')) for sign in block)


def generate_nonce(d_type, block_size: int=16):
    """

    :param d_type:
    :param block_size:
    :return:
    """
    l = list(np.random.randint(0, 255, block_size))
    if d_type == 'int':
        return l
    elif d_type == 'str':
        return hex_string(l)


class AESStringCTR(AESInterface):
    """

    """
    def __init__(self, block_size: int = 16):
        super().__init__()
        self.ctr = 0
        self._nonce = np.zeros(block_size, dtype=int)
        # first half is for nonce rest is for counter
        self.block_size = block_size
        #self._nonce[:block_size//2] = list(np.random.randint(0, 255, block_size//2))
        self._nonce[:block_size//2] = generate_nonce(d_type='int', block_size=block_size//2)

    def nonce(self, i):
        ctr = str(i).zfill(self.block_size//2)
        ctr_block = [ord(i) for i in ctr]
        _nonce = self._nonce
        _nonce[self.block_size//2:] = ctr_block
        return _nonce

    def encrypt(self, text: str) -> str:
        """
        :param text:
        :return:
        """
        # could be simplefied, i don't need the 'block-digits'.
        blocks = text_blocks(text, block_size=32)
        for i, block in enumerate(blocks):
            enc_nonce = encrypt(self.nonce(i), self.expanded_key)
            enc_nonce = hex_string(enc_nonce)
            # print(len(block), len(enc_nonce), i)

            yield xor(block, enc_nonce)

    def decrypt(self, text: str) -> str:
        """
        :param text: encrypted
        :return:
        """
        # two hex-digits -> one sign.
        blocks = text_blocks(text, 32)
        for i, block in enumerate(text):
            dec_nonce = decrypt(self.nonce(i), self.expanded_key)
            # dec_nonce = "".join(str(format(sign, '02x')) for sign in dec_nonce)
            # print(len(block), len(dec_nonce), i)
            # print(dec_nonce, block)
            r = [a ^ b for (a, b) in zip(block, cycle(dec_nonce))]
            #yield r#bytes(xor(block, dec_nonce))#.decode()
            yield bytes([c for c in r])



if __name__ == '__main__':
    my_aes = AESStringCTR()
    my_aes.init_rand_key('8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1')
    my_aes.init_vector = '7950b9c141ad3d6805dea8585bc71b4b'

    test_string = "123456sehr gut. ich bin dann doch etwas müde heute abend und sumpfe hier nur rum ;)"
    # enc = "".join(s for s in my_aes.encrypt(test_string))
    # enc = my_aes.encrypt(test_string)
    enc = list(my_aes.encrypt(test_string))

    print(enc)
    # dec = "".join(s for s in my_aes.decrypt(enc))
    dec =  list(my_aes.decrypt(enc))
    print('decrypted')
    print(dec)
    # print()
    # print('congrats!' if dec == test_string else 'pitty...')
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




