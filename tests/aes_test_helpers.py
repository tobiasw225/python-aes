from collections.abc import Iterable

from python_aes.text_to_number_conversion import random_ints


def assert_blocks_equal(block_a: Iterable, block_b: Iterable):
    for a, b in zip(block_a, block_b, strict=False):
        assert a == b


def sample_nonce(block_size: int) -> list[int]:
    nonce = [0] * block_size
    _nonce: list[int] = list(random_ints(block_size, 0, 255))
    for i, n in enumerate(_nonce):
        nonce[i] = n
    return nonce
