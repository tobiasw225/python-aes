""" """

import binascii
import math
import random
import re
from collections.abc import AsyncGenerator, Generator, Iterable, Sequence
from functools import partial
from typing import Any

import aiofiles


def text_to_ord(text: str) -> list[int]:
    return [ord(c) for c in text]


def string_to_blocks(text: str, block_size: int) -> Generator[Sequence, Any, None]:
    return reshape_blocks(blocks=text_to_ord(text), block_size=block_size)


def text_blocks(text: str, block_size: int) -> Generator[str, Any, None]:
    i = 0
    while i < len(text):
        yield "".join(text[i : i + block_size])
        i += block_size


def reshape_blocks(
    blocks: list, block_size: int = 16
) -> Generator[Sequence, Any, None]:
    """
    reshape blocks from simple list
    to list of lists and add a default-value
    (whitespace : 32)

    :param blocks:
    :param block_size:
    :return:
    """
    max_byte = 255
    max_val = 256
    start = 0
    while len(row := blocks[start : start + block_size]) == block_size:
        if any(e for e in row if e > max_byte):
            raise NotImplementedError(
                f"ord(c) with results higher than 255 are not possible: {row}, {start}"
            )
        yield [0 if e > max_val else e for e in row]
        start += block_size
    # last row might not be full
    last_row = [32] * block_size
    for i in range(len(row)):
        last_row[i] = row[i]
    yield [0 if e > max_val else e for e in row]


def chr_decode(c) -> str:
    try:
        return chr(c)
    # todo better exception
    except Exception:
        return ""


def xor_blocks(a: Iterable, b: Iterable) -> list[int]:
    return [l ^ d for l, d in zip(a, b, strict=False)]  # noqa: E741


def ascii_file_to_blocks(filename: str) -> Generator[Sequence, Any, None]:
    with open(filename) as fin:
        text = fin.read()
    return reshape_blocks(blocks=text_to_ord(text))


def utf_text_file_to_blocks(
    filename: str, encoding: str = "utf-8"
) -> Generator[list[int], Any, None]:
    """
        letters to numbers

    :param filename:
    :param encoding:
    :return:
    """
    end = 4 if encoding == "utf-16" else 16
    with open(filename, "rb") as fin:
        while letters := fin.read(end):
            len_byte = len(letters)
            content = list(letters)
            if len_byte < end:
                # when you have to fill up, it means you've reached eof
                content.extend([0] * (end - len_byte))
            yield content


def hex_string(block) -> str:
    return "".join(str(format(sign, "02x")) for sign in block)


def generate_nonce(d_type: type, block_size: int = 16) -> None | list[int] | str:
    my_nonce = list(random_ints(block_size, 0, 255))
    if d_type is int:
        return my_nonce
    return hex_string(my_nonce)


rand_key = partial(generate_nonce, str)


def process_block(block: str) -> list[int]:
    """splits the string in 2pairs"""
    pairs = re.findall("..", block)
    return [int(x, 16) for x in pairs]


def hex_digits_to_block(key: str) -> list:
    return process_block(key)


def chunks(blocks: Sequence, n: int = 16) -> Generator[Sequence, Any, None]:
    """Yield successive n-sized chunks from blocks."""
    for i in range(0, len(blocks), n):
        yield blocks[i : i + n]


def rstrip_value(value: Any, my_list: list[Any]) -> list[Any]:
    while my_list and my_list[-1] == value:
        my_list.pop(-1)
    return my_list


remove_trailing_zero = partial(rstrip_value, 0)


"""
    byte utils
"""


def fill_byte_block(block: Sequence, block_size: int) -> list:
    block = list(block)
    block.extend([0] * (block_size - len(block)))
    return block


async def blocks_of_file(
    filename: str, block_size: int = 16
) -> AsyncGenerator[list, Any]:
    async with aiofiles.open(filename, mode="rb") as fin:
        while block := await fin.read(block_size):
            yield fill_byte_block(block, block_size)


def blocks_of_string(text: str, block_size: int = 16) -> Generator[str, Any, None]:
    byte_text = bytes(text, "utf-8")
    for _i, block in enumerate(chunks(byte_text, n=block_size)):
        yield bytes(fill_byte_block(block, block_size)).decode("utf-8")


def block_to_byte(block) -> bytes:
    b_block = [hex(number)[2:].zfill(2) for number in block]
    return binascii.unhexlify("".join(b_block))


def random_ints(n: int, start: int = 0, stop: int = -1) -> list[int]:
    gen = random.SystemRandom()
    return [gen.randrange(start=start, stop=stop) for _ in range(n)]


def get_block_size_and_num_rows(block) -> tuple[int, int]:
    block_size = len(block)
    return block_size, int(math.sqrt(block_size))
