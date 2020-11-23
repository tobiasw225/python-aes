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

import numpy as np
import os
from abc import ABC, abstractmethod
from itertools import cycle
from typing import List
from pathlib import Path
from python_aes.aes256 import decrypt, encrypt
from python_aes.helper import (
    chunks,
    get_key,
    hex_string,
    process_block,
    sample_nonce,
    rstrip,
)
from python_aes.key_manager import expand_key
from python_aes.process_bytes import block_to_byte, blocks_of_file, blocks_of_string
from python_aes.text_encoding import chr_decode, string_to_blocks
from python_aes.test.utils import download


class AESInterface(ABC):
    """
        Interface for AES implementations Text & Byte
    """

    def __init__(self):
        self.expanded_key = None
        self.key = None
        self.set_key(key="keys/gKey")
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
    >>> my_aes = AESString()
    >>> enc = "".join(s for s in my_aes.encrypt('test string'))
    >>> dec_string = "".join(s for s in my_aes.decrypt(enc)).rstrip()
    >>> print(dec_string)
    test string
    """

    def __init__(self):
        super().__init__()

    def encrypt(self, text: str) -> str:
        """
        :param text:
        :return:
        """
        last_block = self.init_vector
        blocks = string_to_blocks(text, block_size=16)
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
    """
    >>> filename = "test.svg"
    >>> download(url="https://upload.wikimedia.org/wikipedia/commons/f/ff/Oxygen-actions-im-qq.svg?download",  output_file=filename)
    >>> my_aes = AESBytes()
    >>> enc_file = "test.enc.svg"
    >>> dec_file = "test.dec.svg"
    >>> my_aes.encrypt(filename=filename, output_file=enc_file)
    >>> my_aes.decrypt(filename=enc_file, output_file=dec_file)
    >>> print(Path(filename).stat().st_size == Path(dec_file).stat().st_size)
    True

    """

    def encrypt(self, filename: str, output_file: str):
        """
            encrypts file block by block
            and returns the encrypted byte-string.

        :param filename:
        :return:
        """
        assert os.path.isfile(filename)
        last_block = self.init_vector
        with open(output_file, "wb") as fout:
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
        with open(output_file, "wb") as fout:
            _buffer = None
            for block in blocks_of_file(filename):
                dec_block = decrypt(block, self.expanded_key)
                # cbc (comment out for ecb)
                dec_block = np.bitwise_xor(last_block, dec_block)
                if _buffer is not None:
                    fout.write(block_to_byte(_buffer))
                _buffer = dec_block
                last_block = block
            # last block: remove all trailing elements.
            _buffer = rstrip(_buffer.tolist(), 0)
            fout.write(block_to_byte(_buffer))


class AESCTR(AESInterface):
    def encrypt(self, *args, **kwargs):
        pass

    def decrypt(self, *args, **kwargs):
        pass

    def __init__(self, block_size: int = 16):
        super().__init__()
        self.ctr = 0
        # first half is for nonce, rest is for counter
        self.block_size = block_size
        assert block_size == 16
        self._nonce = sample_nonce(block_size)

    def nonce(self, i):
        ctr = str(i).zfill(self.block_size // 2)
        _nonce = self._nonce
        _nonce[self.block_size // 2 :] = [ord(i) for i in ctr]
        return _nonce

    def set_nonce(self, nonce: str):
        nonce = process_block(nonce)
        assert len(nonce) * 2 == self.block_size
        self._nonce = np.zeros(self.block_size, dtype=int)
        self._nonce[: self.block_size // 2] = nonce


class AESStringCTR(AESCTR):
    """
    >>> my_aes = AESStringCTR()
    >>> my_aes.set_key("8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1")
    >>> my_aes.set_nonce("b2e47dd87113a992")
    >>> test_string = "123456sehr gut."
    >>> enc = my_aes.encrypt(test_string)
    >>> dec = "".join(s for s in my_aes.decrypt(enc))
    >>> print(dec) # doctest: +NORMALIZE_WHITESPACE
        123456sehr gut.
    """

    def __init__(self, block_size: int = 16):
        super().__init__(block_size)

    def encrypt(self, text: str) -> str:
        blocks = blocks_of_string(text, block_size=self.block_size)
        for i, block in enumerate(blocks):
            enc_nonce = encrypt(self.nonce(i), self.expanded_key)
            enc_nonce = hex_string(enc_nonce)
            enc_block = [
                a ^ b
                for (a, b) in zip(
                    bytes(block, "utf-8"), cycle(bytes(enc_nonce, "utf-8"))
                )
            ]
            yield block_to_byte(enc_block)

    def decrypt(self, text_blocks: List[str]) -> str:
        """
        :param text_blocks: encrypted
        :return:
        """
        # b''.join(b) #todo
        # slicing possible
        for i, block in enumerate(text_blocks):
            dec_nonce = encrypt(self.nonce(i), self.expanded_key)
            dec_nonce = hex_string(dec_nonce)
            dec_text = [
                a ^ b for (a, b) in zip(bytes(block), cycle(bytes(dec_nonce, "utf-8")))
            ]
            # remove dangling elements.
            if 0 in dec_text:
                dec_text = list(filter(None, dec_text))
            yield bytes(dec_text).decode()


class AESBytesCTR(AESCTR):
    """
    >>> my_aes = AESBytesCTR()
    >>> filename = "test.svg"
    >>> download(url="https://upload.wikimedia.org/wikipedia/commons/f/ff/Oxygen-actions-im-qq.svg?download",  output_file=filename)
    >>> enc_file = "test.enc.svg"
    >>> dec_file = "test.dec.svg"
    >>> my_aes.set_key("8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1")
    >>> my_aes.set_nonce(\
        "b2e47dd87113a99201a54904c61f7a6f51d1f92187294faf3b5d8e8dd07ce48b"[:16]\
    )
    >>> my_aes.encrypt(filename=filename, output_file=enc_file)
    >>> my_aes.decrypt(filename=enc_file, output_file=dec_file)
    >>> print(Path(filename).stat().st_size == Path(dec_file).stat().st_size)
    True
    """

    def __init__(self, block_size: int = 16):
        super().__init__(block_size)

    def decrypt(self, filename: str, output_file: str):
        with open(output_file, "wb") as fout:
            _buffer = None
            for i, block in enumerate(blocks_of_file(filename)):
                dec_nonce = encrypt(self.nonce(i), self.expanded_key)
                dec_block = [a ^ b for (a, b) in zip(block, cycle(dec_nonce))]
                # remove dangling elements.
                if _buffer is not None:
                    fout.write(block_to_byte(_buffer))
                _buffer = dec_block
            # remove trailing zeros
            _buffer = rstrip(_buffer, 0)
            fout.write(block_to_byte(_buffer))

    def encrypt(self, filename: str, output_file: str):
        assert os.path.isfile(filename)
        with open(output_file, "wb") as fout:
            for i, block in enumerate(blocks_of_file(filename)):
                enc_nonce = encrypt(self.nonce(i), self.expanded_key)
                enc_block = [a ^ b for (a, b) in zip(block, cycle(enc_nonce))]
                fout.write(block_to_byte(enc_block))
