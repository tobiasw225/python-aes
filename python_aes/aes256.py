import asyncio
from collections.abc import Generator, Sequence
from concurrent.futures.process import ProcessPoolExecutor

import aiofiles

from python_aes.column_mixer import mix, mix_invert
from python_aes.key_manager import expand_key
from python_aes.row_shifter import shift
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
    def __init__(self, key: str, block_size: int = DEFAULT_BLOCK_SIZE):
        self.expanded_key: list[int] = self.expand_key(key)
        self.key = None
        self._init_vector = random_ints(block_size, 0, 255)
        self.block_size, self.num_rows = get_block_size_and_num_rows(self._init_vector)

    @property
    def init_vector(self):
        return self._init_vector

    @init_vector.setter
    def init_vector(self, key: str):
        self._init_vector = hex_digits_to_block(key)

    @staticmethod
    def expand_key(key: str) -> list[int]:
        return expand_key(hex_digits_to_block(key))

    def encrypt_block(self, block: Sequence[int]) -> list[int]:
        """Encrypt a single 16-byte block.

        >>> b = list(range(16))
        >>> k = "0" * 64
        >>> crypter = AESBase(key=k)
        >>> enc = crypter.encrypt_block(block=b)
        >>> dec = crypter.decrypt_block(block=enc)
        >>> dec == b
        True

        :param block: input block to encrypt
        :return: encrypted block
        """
        target = len(block) - 1
        for i in range(target):
            ri = self.expanded_key[i : i + self.block_size]
            if i != 0:
                block = shift(
                    block=[sbox[z] for z in block],
                    num_rows=self.num_rows,
                    block_size=self.block_size,
                )
                if i != target - 1:
                    block = mix(block=block, n=self.num_rows)
            block = add_roundkey(block=list(block), round_key=list(ri))
        return list(block)

    def decrypt_block(self, block: Sequence[int]) -> list[int]:
        """Decrypt a single 16-byte block.

        >>> enc = list(range(16))
        >>> k = "0" * 64
        >>> aes = AESBase(key=k)
        >>> dec = aes.decrypt_block(block=enc)
        >>> aes.encrypt_block(block=dec) == enc
        True

        :param block: encrypted block to decrypt
        :return: decrypted block
        """
        target = len(block) - 2
        for i in range(target, -1, -1):
            ri = self.expanded_key[i : i + self.block_size]
            if i == target:
                block = add_roundkey(block=list(block), round_key=list(ri))
            else:
                block = shift(
                    block=list(block),
                    invert=True,
                    num_rows=self.num_rows,
                    block_size=self.block_size,
                )
                block = add_roundkey(
                    block=[sbox_inv[z] for z in block], round_key=list(ri)
                )
                if i != 0:
                    block = mix_invert(block, n=self.num_rows)
        return list(block)


class AESString(AESBase):
    def encrypt(self, text: str) -> Generator[str, None, None]:
        previous_block = self.init_vector
        for raw_block in string_to_blocks(text, block_size=self.block_size):
            xor_block = xor_blocks(raw_block, previous_block)
            previous_block = self.encrypt_block(xor_block)
            yield hex_string(previous_block)

    def decrypt(self, text: str) -> Generator[str, None, None]:
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
                task = loop.run_in_executor(pool, self.encrypt_block, block)
                tasks.append(task)
        blocks = await asyncio.gather(*tasks)
        async with aiofiles.open(output_file, mode="wb") as fout:
            for block in blocks:
                await fout.write(block_to_byte(list(block)))

    async def decrypt(self, filename: str, output_file: str):
        loop = asyncio.get_running_loop()
        tasks = []
        with ProcessPoolExecutor() as pool:
            async for block in blocks_of_file(filename):
                task = loop.run_in_executor(pool, self.decrypt_block, block)
                tasks.append(task)

        blocks = await asyncio.gather(*tasks)
        async with aiofiles.open(output_file, mode="wb") as fout:
            for block in blocks[:-1]:
                await fout.write(block_to_byte(list(block)))
            if blocks:
                await fout.write(block_to_byte(remove_trailing_zero(list(blocks[-1]))))


class AESBytesCBC(AESBase):
    async def encrypt(self, filename: str, output_file: str):
        previous_block: list[int] = self.init_vector
        async with aiofiles.open(output_file, mode="wb") as fout:
            async for block in blocks_of_file(filename):
                xored: list[int] = xor_blocks(block, previous_block)
                previous_block = self.encrypt_block(list(xored))
                await fout.write(block_to_byte(list(previous_block)))

    async def decrypt(self, filename: str, output_file: str):
        previous_block: list[int] = self.init_vector
        next_decrypted_block: list[int] | None = None
        async with aiofiles.open(output_file, mode="wb") as fout:
            async for block in blocks_of_file(filename):
                dec_block = self.decrypt_block(list(block))
                xored_block: list[int] = xor_blocks(previous_block, dec_block)
                if next_decrypted_block is not None:
                    await fout.write(block_to_byte(list(next_decrypted_block)))
                next_decrypted_block = xored_block
                previous_block = list(block)
            if next_decrypted_block is not None:
                await fout.write(
                    block_to_byte(remove_trailing_zero(list(next_decrypted_block)))
                )


def add_roundkey(round_key: list[int], block: list[int]) -> list[int]:
    return list(xor_blocks(round_key, block))
