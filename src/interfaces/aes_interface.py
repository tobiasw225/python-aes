#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: aes_interface.py
#
# __description__: use this class to encrypt/ decrypt strings with aes256
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2017
# Copyright (c) 2017 Tobias Wenzel
import random
import os
from abc import ABC, abstractmethod

from aes256 import decrypt, encrypt
from utils import hex_string, process_block, hex_digits_to_block, chunks, remove_trailing_zero, block_to_byte, \
    blocks_of_file, chr_decode, string_to_blocks, random_ints
from key_manager import expand_key

from src.utils import xor_blocks


class AESInterface(ABC):
    """
        Interface for AES implementations Text & Byte
    """

    def __init__(self):
        self.expanded_key = None
        self.key = None
        self._init_vector = random_ints(16, 0, 255)

    @property
    def init_vector(self):
        return self._init_vector

    @init_vector.setter
    def init_vector(self, key: str):
        self._init_vector = hex_digits_to_block(key)

    def set_key(self, key: str):
        """
            The key can be either a file (plain-text hex-digits)
            or passed as string.

        :param key
        :return:
        """
        self.key = hex_digits_to_block(key)
        self.expanded_key = expand_key(self.key)

    @abstractmethod
    def encrypt(self, *args, **kwargs):
        pass

    @abstractmethod
    def decrypt(self, *args, **kwargs):
        pass


class AESString(AESInterface):
    def __init__(self):
        super().__init__()

    def encrypt(self, text: str) -> str:
        last_block = self.init_vector
        for block in string_to_blocks(text, block_size=16):
            last_block = list(last_block)
            block = xor_blocks(block, last_block)
            last_block = encrypt(block, self.expanded_key)
            yield hex_string(last_block)

    def decrypt(self, text: str) -> str:
        last_block = self.init_vector
        blocks = process_block(text)
        for block in chunks(blocks):
            dec_block = decrypt(block, self.expanded_key)
            last_block = xor_blocks(last_block, dec_block)
            yield "".join([chr_decode(c) for c in last_block])
            last_block = block


class AESBytes(AESInterface):
    def encrypt(self, filename: str, output_file: str):
        """
            encrypts file block by block

        :param output_file:
        :param filename:
        :return:
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError

        last_block = self.init_vector
        with open(output_file, "wb") as fout:
            for block in blocks_of_file(filename):
                # cbc (comment out for ecb)
                block = xor_blocks(block, last_block)
                last_block = encrypt(block, self.expanded_key)
                fout.write(block_to_byte(last_block))

    def decrypt(self, filename: str, output_file: str):
        """

        :param filename:
        :param output_file:
        :return:
        """
        last_block = self.init_vector
        with open(output_file, "wb") as fout:
            _buffer = None
            for block in blocks_of_file(filename):
                dec_block = decrypt(block, self.expanded_key)
                # cbc (comment out for ecb)
                dec_block = xor_blocks(last_block, dec_block)
                if _buffer is not None:
                    fout.write(block_to_byte(_buffer))
                _buffer = dec_block
                last_block = block
            # last block: remove all trailing elements.
            _buffer = remove_trailing_zero(_buffer)
            fout.write(block_to_byte(_buffer))
