import re
from collections.abc import Generator, Sequence
from itertools import cycle

from python_aes.aes256 import AESBase
from python_aes.exceptions import AESError
from python_aes.text_to_number_conversion import (
    block_to_byte,
    blocks_of_file,
    blocks_of_string,
    hex_string,
    remove_trailing_zero,
    xor_blocks,
)
from python_aes.utils import async_enumerate


class CounterMode(AESBase):
    def __init__(self, key: str, block_size: int):
        super().__init__(block_size=block_size, key=key)
        self.ctr = 0
        # first half is for nonce, rest is for counter
        self.block_size = block_size
        self._nonce = [0] * self.block_size

    def nonce(self, i: int) -> list[int]:
        ctr = str(i).zfill(self.block_size // 2)
        _nonce = self._nonce
        _nonce[self.block_size // 2 :] = [ord(i) for i in ctr]
        return _nonce

    def set_nonce(self, nonce: Sequence[int] | str) -> None:
        if isinstance(nonce, str):
            nonce = process_block(nonce)
        if len(nonce) * 2 != self.block_size:
            raise AESError("len(nonce)*2 should be twice the block size.")
        self._nonce[: self.block_size // 2] = nonce


def process_block(block: str) -> list[int]:
    pairs = re.findall("..", block)
    return [int(x, 16) for x in pairs]


class StringCounterMode(CounterMode):
    def encrypt(self, text: str) -> Generator[bytes, None, None]:
        blocks = blocks_of_string(text, block_size=self.block_size)
        for i, block in enumerate(blocks):
            enc_nonce = self.encrypt_block(self.nonce(i))
            enc_nonce_bytes = [ord(c) for c in hex_string(enc_nonce)]
            enc_block = [
                a ^ b for (a, b) in zip([ord(c) for c in block], cycle(enc_nonce_bytes))
            ]
            yield block_to_byte(enc_block)

    def decrypt(self, text_blocks: Sequence[bytes]) -> Generator[str, None, None]:
        for i, block in enumerate(text_blocks):
            dec_nonce = self.encrypt_block(self.nonce(i))
            dec_nonce_bytes: list[int] = [ord(c) for c in hex_string(dec_nonce)]
            dec_text = xor_blocks(list(block), cycle(dec_nonce_bytes))
            if 0 in dec_text:
                dec_text = list(filter(None, dec_text))
            yield bytes(dec_text).decode()


class ByteCounterMode(CounterMode):
    def __init__(self, block_size: int, key: str):
        super().__init__(block_size=block_size, key=key)

    async def decrypt(self, filename: str, output_file: str):
        with open(output_file, "wb") as fout:
            _buffer = None
            async for i, block in async_enumerate(blocks_of_file(filename)):
                dec_nonce = self.encrypt_block(self.nonce(i))
                dec_block = xor_blocks(block, cycle(dec_nonce))
                if _buffer:
                    fout.write(block_to_byte(_buffer))
                _buffer = dec_block
            if _buffer is not None:
                _buffer = remove_trailing_zero(_buffer)
                fout.write(block_to_byte(_buffer))

    async def encrypt(self, filename: str, output_file: str):
        with open(output_file, "wb") as fout:
            async for i, block in async_enumerate(blocks_of_file(filename)):
                enc_nonce = self.encrypt_block(self.nonce(i))
                enc_block = xor_blocks(block, cycle(enc_nonce))
                fout.write(block_to_byte(enc_block))
