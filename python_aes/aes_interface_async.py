#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: aes_interface_async.py
#
# __description__: use this class to encrypt/ decrypt strings with aes256
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2017
# Copyright (c) 2017 Tobias Wenzel
import aiofiles as aiof
import asyncio
import numpy as np
import os
from abc import ABC, abstractmethod
from itertools import cycle
from typing import List
from pathlib import Path
from python_aes.aes256 import decrypt, encrypt
from python_aes.helper import chunks, get_key, hex_string, process_block, sample_nonce
from python_aes.key_manager import expand_key
from python_aes.process_bytes import (
    block_to_byte,
    blocks_of_file,
    fill_byte_block,
    blocks_of_string,
)
from python_aes.text_encoding import chr_decode, string_to_blocks


# async def blocks_of_file(filename: str, block_size: int = 16) -> np.ndarray:
#     assert os.path.isfile(filename)
#     async with aiof.open(file=filename, mode="rb") as fin:
#         while block := await fin.read(block_size):
#             yield np.array(fill_byte_block(block, block_size))


class AESInterface(ABC):
    """
        Interface for AES implementations Text & Byte
    """

    def __init__(self, block_size: int = 16):
        self.expanded_key = None
        self.key = None
        self.block_size = block_size
        self.set_key(key="/home/tobias/mygits/python-aes/keys/gKey")
        self._init_vector = np.random.randint(0, 255, self.block_size)

    @property
    def init_vector(self):
        return self._init_vector

    @init_vector.setter
    def init_vector(self, key: str):
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
        pass

    @abstractmethod
    def decrypt(self, *args, **kwargs):
        pass


class AESStringECB(AESInterface):
    """
        # >>> my_aes = AESStringECB(16)
        # >>> loop = asyncio.get_event_loop()
        # >>> enc_blocks = loop.run_until_complete(my_aes.encrypt(loop, 'test string'*3))
        # >>> enc_string = "".join(block.result() for block in enc_blocks)
        # >>> dec_blocks = loop.run_until_complete(my_aes.decrypt(loop, enc_string))
        # >>> dec_string = "".join(block.result() for block in dec_blocks)
        # >>> print(dec_string) # doctest: +NORMALIZE_WHITESPACE
        #         test stringtest stringtest string
        # >>> loop.close()
    """

    def __init__(self, block_size):
        super().__init__(block_size)

    async def encrypt_wrapper(self, block) -> str:
        enc_block = encrypt(block, self.expanded_key)
        return hex_string(enc_block)

    async def encrypt(self, loop, text: str) -> List:
        # todo passing loop to pass doc-test: not very nice, i think.
        blocks = string_to_blocks(text, block_size=16)
        events = []
        for block in blocks:
            events.append(loop.create_task(self.encrypt_wrapper(block)))
        await asyncio.wait(events)
        return events

    async def decrypt_wrapper(self, block):
        dec_block = decrypt(block, self.expanded_key)
        return "".join([chr_decode(c) for c in dec_block])

    async def decrypt(self, loop, text: str) -> List:
        blocks = process_block(text)
        assert len(blocks) % 16 == 0
        events = []
        for block in np.array_split(blocks, len(blocks) / 16):
            events.append(loop.create_task(self.decrypt_wrapper(block)))
        await asyncio.wait(events)
        return events


class AESBytesECB(AESInterface):
    """
    # >>> my_aes = AESBytes()
    # >>> filename = "res/test.jpg"
    # >>> output_file = "res/test.enc.jpg"
    # >>> dec_file = "res/test.dec.jpg"
    # >>> my_aes.encrypt(filename=filename, output_file=output_file)
    # >>> my_aes.decrypt(filename=output_file, output_file=dec_file)
    # >>> print(Path(filename).stat().st_size == Path(dec_file).stat().st_size)
    # True

    """

    async def encrypt(self, filename: str, output_file: str):
        assert os.path.isfile(filename)
        async with aiof.open(output_file, "wb") as fout:
            async with aiof.open(file=filename, mode="rb") as fin:
                while block := await fin.read(self.block_size):
                    block = np.array(fill_byte_block(block, self.block_size))
                    last_block = encrypt(block, self.expanded_key)
                    await fout.write(block_to_byte(last_block))

    async def decrypt(self, filename: str, output_file: str):
        async with aiof.open(output_file, "wb") as fout:
            _buffer = None
            async with aiof.open(file=filename, mode="rb") as fin:
                while block := await fin.read(self.block_size):
                    block = np.array(fill_byte_block(block, self.block_size))
                    dec_block = decrypt(block, self.expanded_key)
                    if _buffer is not None:
                        await fout.write(block_to_byte(_buffer))
                    _buffer = dec_block
            # last block: remove all dangling elements.
            _buffer = np.array(list(filter(lambda x: x != 0, _buffer)))
            await fout.write(block_to_byte(_buffer))


class AESStringCTR(AESInterface):
    """
    # >>> my_aes = AESStringCTR(16)
    # >>> my_aes.set_key("8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1")
    # >>> my_aes.set_nonce(\
    #     "b2e47dd87113a99201a54904c61f7a6f51d1f92187294faf3b5d8e8dd07ce48b"[:16]\
    # )
    # >>> test_string = "123456sehr gut."
    # >>> loop = asyncio.get_event_loop()
    # >>> enc_blocks = loop.run_until_complete(my_aes.encrypt(loop, text=test_string))
    # >>> enc_blocks= [block.result() for block in enc_blocks]
    # >>> dec_blocks = loop.run_until_complete(my_aes.decrypt(loop, text_blocks=enc_blocks))
    # >>> dec_string = "".join(block.result() for block in dec_blocks)
    # >>> print(dec_string) # doctest: +NORMALIZE_WHITESPACE
    #     123456sehr gut.
    # >>> loop.close()
    """

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

    async def encrypt_wrapper(self, block, i):
        enc_nonce = encrypt(self.nonce(i), self.expanded_key)
        enc_nonce = hex_string(enc_nonce)
        enc_block = [
            a ^ b
            for (a, b) in zip(bytes(block, "utf-8"), cycle(bytes(enc_nonce, "utf-8")))
        ]
        return block_to_byte(enc_block)

    async def encrypt(self, loop, text: str) -> List:
        blocks = blocks_of_string(text, block_size=self.block_size)
        events = []
        for i, block in enumerate(blocks):
            events.append(loop.create_task(self.encrypt_wrapper(block, i)))
        await asyncio.wait(events)
        return events

    async def decrypt_wrapper(self, block, i):
        dec_nonce = encrypt(self.nonce(i), self.expanded_key)
        dec_nonce = hex_string(dec_nonce)
        dec_text = [
            a ^ b for (a, b) in zip(bytes(block), cycle(bytes(dec_nonce, "utf-8")))
        ]
        # remove dangling elements.
        if 0 in dec_text:
            dec_text = list(filter(None, dec_text))
        return bytes(dec_text).decode()

    async def decrypt(self, loop, text_blocks: List[str]) -> List:
        # b''.join(b)
        # slicing possible
        events = []
        for i, block in enumerate(text_blocks):
            events.append(loop.create_task(self.decrypt_wrapper(block, i)))
        await asyncio.wait(events)
        return events


if __name__ == "__main__":
    # i think i need some sleep.
    try:
        loop = asyncio.get_event_loop()
        my_aes = AESBytesECB()
        filename = "../res/test.jpg"
        output_file = "../res/test.enc.jpg"
        dec_file = "../res/test.dec.jpg"
        loop.run_until_complete(my_aes.encrypt(filename, output_file))
        loop.run_until_complete(my_aes.decrypt(output_file, dec_file))

    except Exception as e:
        raise e
    finally:
        loop.close()
