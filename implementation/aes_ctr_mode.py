from itertools import cycle
from typing import List

from implementation.aes256 import AESBase
from utils import (block_to_byte, blocks_of_file, blocks_of_string, hex_string,
                   process_block, remove_trailing_zero, xor_blocks)


class CounterMode(AESBase):
    def encrypt(self, *args, **kwargs):
        pass

    def decrypt(self, *args, **kwargs):
        pass

    def __init__(self, block_size: int = 16):
        super().__init__()
        self.ctr = 0
        # first half is for nonce, rest is for counter
        # todo other block-sizes
        if block_size != 16:
            raise NotImplementedError("Blocksize != 16 are not supported yet.")
        self.block_size = block_size
        self._nonce = [0] * self.block_size

    def nonce(self, i):
        ctr = str(i).zfill(self.block_size // 2)
        _nonce = self._nonce
        _nonce[self.block_size // 2 :] = [ord(i) for i in ctr]
        return _nonce

    def set_nonce(self, nonce):
        if type(nonce) is str:
            nonce = process_block(nonce)

        if len(nonce) * 2 != self.block_size:
            raise ValueError(f"len(nonce)*2 should be twice the block size.")
        self._nonce[: self.block_size // 2] = nonce


class StringCounterMode(CounterMode):
    def __init__(self, block_size: int = 16):
        super().__init__(block_size)

    def encrypt(self, text: str) -> str:
        blocks = blocks_of_string(text, block_size=self.block_size)
        for i, block in enumerate(blocks):
            enc_nonce = self.encrypt_block(self.nonce(i), self.expanded_key)
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
            dec_nonce = self.encrypt_block(self.nonce(i), self.expanded_key)
            dec_nonce = hex_string(dec_nonce)
            dec_text = xor_blocks(bytes(block), cycle(bytes(dec_nonce, "utf-8")))
            # remove dangling elements.
            if 0 in dec_text:
                dec_text = list(filter(None, dec_text))
            yield bytes(dec_text).decode()


class ByteCounterMode(CounterMode):
    def __init__(self, block_size: int = 16):
        super().__init__(block_size)

    def decrypt(self, filename: str, output_file: str):
        with open(output_file, "wb") as fout:
            _buffer = None
            for i, block in enumerate(blocks_of_file(filename)):
                dec_nonce = self.encrypt_block(self.nonce(i), self.expanded_key)
                dec_block = xor_blocks(block, cycle(dec_nonce))
                # remove dangling elements.
                if _buffer:
                    fout.write(block_to_byte(_buffer))
                _buffer = dec_block
            _buffer = remove_trailing_zero(_buffer)
            fout.write(block_to_byte(_buffer))

    def encrypt(self, filename: str, output_file: str):
        with open(output_file, "wb") as fout:
            for i, block in enumerate(blocks_of_file(filename)):
                enc_nonce = self.encrypt_block(self.nonce(i), self.expanded_key)
                enc_block = xor_blocks(block, cycle(enc_nonce))
                fout.write(block_to_byte(enc_block))
