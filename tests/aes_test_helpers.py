from collections.abc import Iterable

from python_aes.text_to_number_conversion import generate_nonce


def assert_blocks_equal(block_a: Iterable, block_b: Iterable):
    for a, b in zip(block_a, block_b, strict=False):
        assert a == b


def sample_nonce(block_size: int) -> list[int]:
    nonce = [0] * block_size
    _nonce: list[int] = generate_nonce(d_type=int, block_size=block_size // 2)  # type: ignore[assignment]
    for i, n in enumerate(_nonce):
        nonce[i] = n
    return nonce
