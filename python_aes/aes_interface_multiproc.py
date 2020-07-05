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

import functools
from typing import Generator
import multiprocessing as mp
import operator
import os
from abc import abstractmethod
from itertools import cycle
from pathlib import Path
from typing import List

import numpy as np

from python_aes.aes256 import decrypt, encrypt
from python_aes.aes_interface import AESInterface
from python_aes.helper import chunks
from python_aes.helper import (hex_string, process_block,
                               sample_nonce)
from python_aes.process_bytes import (block_to_byte, blocks_of_file,
                                      blocks_of_string)


class AESInterfaceMultiproc(AESInterface):
    """
        Interface for AES implementations Text & Byte
    """

    def __init__(self):
        super().__init__()
        self.num_pools = mp.cpu_count()

    @abstractmethod
    def encrypt_batch(self, batch: List[List]) -> List:
        pass

    @abstractmethod
    def decrypt_batch(self, batch: List[List]) -> List:
        pass

    def start_batch_process(self, func: callable,
                            blocks: Generator) -> List:
        pool = mp.Pool(self.num_pools)
        blocks = list(blocks)
        batches = (batch for batch in chunks(blocks, n=len(blocks)//self.num_pools))
        results = [pool.map(func,
                            (batch for batch in batches))]
        pool.close()
        return functools.reduce(operator.iconcat, results[0], [])

    def encryption_processes(self, blocks: Generator) -> List:
        return self.start_batch_process(self.encrypt_batch, blocks)

    def decryption_processes(self, blocks: Generator) -> List:
        return self.start_batch_process(self.decrypt_batch, blocks)


class AESBytesECB(AESInterfaceMultiproc):
    """
    >>> my_aes = AESBytesECB()
    >>> filename = "res/test.jpg"
    >>> output_file = "res/test.enc.jpg"
    >>> dec_file = "res/test.dec.jpg"
    >>> my_aes.encrypt(filename=filename, output_file=output_file)
    >>> my_aes.decrypt(filename=output_file, output_file=dec_file)
    >>> print(Path(filename).stat().st_size == Path(dec_file).stat().st_size)
    True

    """
    def encrypt_batch(self, batch: List[np.ndarray]) -> List:
        return [block_to_byte(encrypt(block, self.expanded_key))
                for block in batch]

    def encrypt(self, filename: str, output_file: str):
        assert os.path.isfile(filename)
        blocks = (block for block in blocks_of_file(filename))
        with open(output_file, "wb") as fout:
            for block in self.encryption_processes(blocks):
                fout.write(block)

    def decrypt_batch(self, batch: List[np.ndarray]) -> List:
        return [block_to_byte(decrypt(block, self.expanded_key))
                for block in batch]

    def decrypt(self, filename: str, output_file: str):
        with open(output_file, "wb") as fout:
            _buffer = None
            blocks = (block for block in blocks_of_file(filename))
            for dec_block in self.decryption_processes(blocks):
                if _buffer:
                    fout.write(_buffer)
                _buffer = dec_block
            # last block: remove all dangling elements.
            _buffer = block_to_byte(np.array(list(filter(lambda x: x != 0, _buffer))))
            fout.write(_buffer)


class AESStringCTR(AESInterfaceMultiproc):
    """
    >>> my_aes = AESStringCTR()
    >>> my_aes.set_key("8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1")
    >>> my_aes.init_vector = "7950b9c141ad3d6805dea8585bc71b4b"
    >>> my_aes.set_nonce(\
        "b2e47dd87113a99201a54904c61f7a6f51d1f92187294faf3b5d8e8dd07ce48b"[:16]\
    )
    >>> test_string = "123456sehr gut."
    >>> enc = my_aes.encrypt(test_string)
    >>> dec = "".join(s for s in my_aes.decrypt(enc))
    >>> print(dec) # doctest: +NORMALIZE_WHITESPACE
        123456sehr gut.
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
        _nonce[self.block_size // 2:] = [ord(i) for i in ctr]
        return _nonce

    def set_nonce(self, nonce: str):
        nonce = process_block(nonce)
        assert len(nonce) * 2 == self.block_size
        self._nonce = np.zeros(self.block_size, dtype=int)
        self._nonce[: self.block_size // 2] = nonce

    def encrypt_batch(self, batch):
        encrypted = []
        for i, block in batch:
            enc_nonce = encrypt(self.nonce(i), self.expanded_key)
            enc_nonce = hex_string(enc_nonce)
            enc_block = [
                a ^ b
                for (a, b) in zip(
                    bytes(block, "utf-8"), cycle(bytes(enc_nonce, "utf-8"))
                )
            ]
            encrypted.append(block_to_byte(enc_block))
        return encrypted

    def encrypt(self, text: str) -> List[bytes]:
        blocks = ((i, block)
                  for i, block in enumerate(blocks_of_string(text,
                                                             block_size=self.block_size)))
        return self.encryption_processes(blocks)

    def decrypt_batch(self, batch):
        decrypted = []
        for i, block in batch:
            dec_nonce = encrypt(self.nonce(i), self.expanded_key)
            dec_nonce = hex_string(dec_nonce)
            dec_text = [
                a ^ b for (a, b) in zip(bytes(block), cycle(bytes(dec_nonce, "utf-8")))
            ]
            # remove dangling elements.
            if 0 in dec_text:
                dec_text = list(filter(None, dec_text))
            decrypted.append(bytes(dec_text).decode())
        return decrypted

    def decrypt(self, text_blocks: List[bytes]) -> List[str]:
        """
        :param text_blocks: encrypted
        :return:
        """
        # b''.join(b)
        # slicing possible
        blocks = ((i, block) for i, block in enumerate(text_blocks))
        return self.decryption_processes(blocks)



if __name__ == '__main__':
    my_aes = AESStringCTR()
    my_aes.set_key("8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1")
    my_aes.init_vector = "7950b9c141ad3d6805dea8585bc71b4b"
    my_aes.set_nonce(\
        "b2e47dd87113a99201a54904c61f7a6f51d1f92187294faf3b5d8e8dd07ce48b"[:16]\
    )
    # 114.81927061080933s: "123456sehr gut."*100000
    # -> 1.9 min
    # test_string = "123456sehr gut."*100
    # import time
    # start = time.time()
    # enc = my_aes.encrypt(test_string)
    # print(time.time()-start)
    # start = time.time()
    # dec_result = my_aes.decrypt(enc)
    # print(time.time() - start)
    # dec = "".join(s for s in dec_result)
    # print(dec)


    my_aes = AESBytesECB()
    filename = "../res/test.jpg"
    output_file = "../res/test.enc.jpg"
    dec_file = "../res/test.dec.jpg"
    import time
    start = time.time()
    my_aes.encrypt(filename=filename, output_file=output_file)
    print(time.time()- start)
    start = time.time()
    my_aes.decrypt(filename=output_file, output_file=dec_file)
    print(time.time()- start)
    print(Path(filename).stat().st_size == Path(dec_file).stat().st_size)

    # done refactor batches
    # todo string pools
    # todo bytes cbc