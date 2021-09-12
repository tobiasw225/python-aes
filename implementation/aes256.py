#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: aes256.py
#
# __description__: use this class to encrypt/ decrypt strings with aes256
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2017
# Copyright (c) 2017 Tobias Wenzel
import os
from abc import abstractmethod
from typing import List

from base.key_manager import expand_key
from base.steps import BlockShifter, ColumnMixer, add_roundkey
from base.tables import sbox, sbox_inv
from base.utils import (block_to_byte, blocks_of_file, chr_decode, chunks,
                        get_block_size_and_num_rows, hex_digits_to_block,
                        hex_string, process_block, random_ints,
                        remove_trailing_zero, string_to_blocks, xor_blocks)


class AESBase:
    """
    Interface for AES implementations Text & Byte
    """

    def __init__(self, block_size: int = 16):
        self.expanded_key = None
        self.key = None
        self._init_vector = random_ints(block_size, 0, 255)
        self.block_size, self.num_rows = get_block_size_and_num_rows(self._init_vector)
        self.block_shifter = BlockShifter(
            num_rows=self.num_rows, block_size=self.block_size
        )
        self.column_mixer = ColumnMixer(
            num_rows=self.num_rows, block_size=self.block_size
        )

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

    def encrypt_block(self, block: List[int], expanded_key: List[int]) -> List[int]:
        """
        >>> key = [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9,\
         10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,\
          25, 26, 27, 28, 29, 30, 31]
        >>> block = [  0,  17,  34,  51,  68,  85, 102, 119,\
         136, 153, 170, 187, 204, 221, 238, 255]
        >>> crypter = AESBase()
        >>> enc = crypter.encrypt_block(block=block,expanded_key=key)
        >>> dec = crypter.decrypt_block(block=enc,expanded_key=key)
        >>> print(dec.__repr__())
        [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]

        :param block:
        :param expanded_key:
        :return: encrypted array
        """
        for i in range(15):
            ri = expanded_key[i : i + self.block_size]
            if i != 0:
                block = [sbox[z] for z in block]
                block = self.block_shifter.shift(block)
                if i != 14:
                    block = self.column_mixer.mix(block)
            block = add_roundkey(block=block, round_key=ri)
        return block

    def decrypt_block(self, block: List[int], expanded_key: List[int]) -> List[int]:
        """
        >>> key = [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10,\
         11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,\
          27, 28, 29, 30, 31]
        >>> enc = [  0,  17,  34,  51,  68,  85, 102, 119, 136,\
         153, 170, 187, 204, 221, 238, 255]
        >>> aes = AESBase()
        >>> dec = aes.decrypt_block(block=enc,expanded_key=key)
        >>> enc = aes.encrypt_block(block=dec,expanded_key=key)
        >>> print(enc.__repr__()) # doctest: +NORMALIZE_WHITESPACE
        [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]

        :param block:
        :param expanded_key:
        :return: decrypted array
        """
        for i in range(14, -1, -1):
            ri = expanded_key[i : i + self.block_size]
            if i == 14:
                block = add_roundkey(block=block, round_key=ri)
            else:
                block = self.block_shifter.shift(block, invert=True)
                block = [sbox_inv[z] for z in block]
                block = add_roundkey(block=block, round_key=ri)
                if i != 0:
                    block = self.column_mixer.mix_invert(block)
        return block


class AESString(AESBase):
    def __init__(self):
        super().__init__()

    def encrypt(self, text: str) -> str:
        last_block = self.init_vector
        for block in string_to_blocks(text, block_size=self.block_size):
            last_block = list(last_block)
            block: List[int] = xor_blocks(block, last_block)
            last_block = self.encrypt_block(block, self.expanded_key)
            yield hex_string(last_block)

    def decrypt(self, text: str) -> str:
        last_block = self.init_vector
        blocks = process_block(text)
        for block in chunks(blocks):
            dec_block = self.decrypt_block(block, self.expanded_key)
            last_block = xor_blocks(last_block, dec_block)
            yield "".join([chr_decode(c) for c in last_block])
            last_block = block


class AESBytes(AESBase):
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
                last_block = self.encrypt_block(block, self.expanded_key)
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
                dec_block = self.decrypt_block(block, self.expanded_key)
                # cbc (comment out for ecb)
                dec_block = xor_blocks(last_block, dec_block)
                if _buffer is not None:
                    fout.write(block_to_byte(_buffer))
                _buffer = dec_block
                last_block = block
            # last block: remove all trailing elements.
            _buffer = remove_trailing_zero(_buffer)
            fout.write(block_to_byte(_buffer))
