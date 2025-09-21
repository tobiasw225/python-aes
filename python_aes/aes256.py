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
import asyncio
from concurrent.futures.process import ProcessPoolExecutor
from typing import Iterable, Any, Generator

import aiofiles

from python_aes.key_manager import expand_key
from python_aes.steps import BlockShifter, ColumnMixer, add_roundkey
from python_aes.tables import sbox, sbox_inv
from python_aes.text_to_number_conversion import (
    block_to_byte,
    blocks_of_file,
    chr_decode,
    chunks,
    get_block_size_and_num_rows,
    hex_digits_to_block,
    hex_string,
    process_block,
    random_ints,
    remove_trailing_zero,
    string_to_blocks,
    xor_blocks,
)

DEFAULT_BLOCK_SIZE = 16


class AESBase:
    """
    Interface for AES implementations Text & Byte
    """

    def __init__(self, key: str, block_size: int = DEFAULT_BLOCK_SIZE):
        self.expanded_key: list[int] = self.expand_key(key)
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

    @staticmethod
    def expand_key(key: str) -> list[int]:
        """
        The key can be either a file (plain-text hex-digits)
        or passed as string.
        # TODO: this is too obscure!
        """
        _key = hex_digits_to_block(key)
        return expand_key(_key)

    def encrypt_block(self, block: Iterable[int]) -> Iterable[int]:
        """
        >>> block = [  0,  17,  34,  51,  68,  85, 102, 119,\
         136, 153, 170, 187, 204, 221, 238, 255]
        >>> crypter = AESBase()
        >>> enc = crypter.encrypt_block(block=block)
        >>> dec = crypter.decrypt_block(block=enc)
        >>> print(dec.__repr__())
        [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]

        :param block:
        :return: encrypted array
        """
        # todo check: this seems kind of random
        target = len(block) - 1
        for i in range(target):
            ri = self.expanded_key[i : i + self.block_size]
            if i != 0:
                block = [sbox[z] for z in block]
                block = self.block_shifter.shift(block)
                if i != target - 1:
                    block = self.column_mixer.mix(block)
            block = add_roundkey(block=block, round_key=ri)
        return block

    def decrypt_block(self, block: Iterable[int]) -> Iterable[int]:
        """
        >>> enc = [  0,  17,  34,  51,  68,  85, 102, 119, 136,\
         153, 170, 187, 204, 221, 238, 255]
        >>> aes = AESBase()
        >>> dec = aes.decrypt_block(block=enc)
        >>> enc = aes.encrypt_block(block=dec)
        >>> print(enc.__repr__()) # doctest: +NORMALIZE_WHITESPACE
        [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]

        :param block:
        :return: decrypted array
        """
        # todo check
        target = len(block) - 2
        for i in range(target, -1, -1):
            ri = self.expanded_key[i : i + self.block_size]
            if i == target:
                block = add_roundkey(block=block, round_key=ri)
            else:
                block = self.block_shifter.shift(block, invert=True)
                block = [sbox_inv[z] for z in block]
                block = add_roundkey(block=block, round_key=ri)
                if i != 0:
                    block = self.column_mixer.mix_invert(block)
        return block


class AESString(AESBase):
    def encrypt(self, text: str) -> Generator[str, Any, None]:
        previous_block = self.init_vector
        for block in string_to_blocks(text, block_size=self.block_size):
            block = xor_blocks(block, previous_block)
            previous_block = self.encrypt_block(block)
            yield hex_string(previous_block)

    def decrypt(self, text: str) -> Generator[str, Any, None]:
        previous_block = self.init_vector
        blocks = process_block(text)
        for block in chunks(blocks):
            dec_block = self.decrypt_block(block)
            previous_block = xor_blocks(previous_block, dec_block)
            yield "".join(chr_decode(c) for c in previous_block)
            previous_block = block


class AESBytesECB(AESBase):
    async def encrypt(self, filename: str, output_file: str):
        loop = asyncio.get_running_loop()
        tasks = []
        with ProcessPoolExecutor() as pool:
            async for block in blocks_of_file(filename):
                task = loop.run_in_executor(
                    pool,
                    self.encrypt_block,
                    block,
                )
                tasks.append(task)
        blocks = await asyncio.gather(*tasks)
        async with aiofiles.open(output_file, mode="wb") as fout:
            for block in blocks:
                await fout.write(block_to_byte(block))

    async def decrypt(self, filename: str, output_file: str):
        loop = asyncio.get_running_loop()
        tasks = []
        with ProcessPoolExecutor() as pool:
            async for block in blocks_of_file(filename):
                task = loop.run_in_executor(
                    pool,
                    self.decrypt_block,
                    block,
                )
                tasks.append(task)

        blocks = await asyncio.gather(*tasks)
        async with aiofiles.open(output_file, mode="wb") as fout:
            for block in blocks[:-1]:
                await fout.write(block_to_byte(block))
            await fout.write(block_to_byte(remove_trailing_zero(blocks[-1])))


class AESBytesCBC(AESBase):
    async def encrypt(self, filename: str, output_file: str):
        previous_block = self.init_vector
        async with aiofiles.open(output_file, mode="wb") as fout:
            async for block in blocks_of_file(filename):
                block = xor_blocks(block, previous_block)
                previous_block = self.encrypt_block(block)
                await fout.write(block_to_byte(previous_block))

    async def decrypt(self, filename: str, output_file: str):
        previous_block = self.init_vector
        async with aiofiles.open(output_file, mode="wb") as fout:
            next_decrypted_block = None
            async for block in blocks_of_file(filename):
                dec_block = self.decrypt_block(block=block)
                dec_block = xor_blocks(previous_block, dec_block)
                if next_decrypted_block is not None:
                    await fout.write(block_to_byte(next_decrypted_block))
                next_decrypted_block = dec_block
                previous_block = block
            await fout.write(block_to_byte(remove_trailing_zero(next_decrypted_block)))
