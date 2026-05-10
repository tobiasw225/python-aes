import filecmp
import tempfile

import pytest

from python_aes.aes256 import DEFAULT_BLOCK_SIZE
from python_aes.aes_ctr_mode import ByteCounterMode, StringCounterMode
from tests.aes_test_helpers import sample_nonce


async def test_ctr_mode_bytes_complete(small_byte_file, default_hex_key):
    my_aes = ByteCounterMode(key=default_hex_key, block_size=DEFAULT_BLOCK_SIZE)
    my_aes.set_nonce(sample_nonce(8))
    with (
        small_byte_file as in_file,
        tempfile.NamedTemporaryFile() as enc_file,
        tempfile.NamedTemporaryFile() as dec_file,
    ):  # noqa: E501
        await my_aes.encrypt(filename=in_file.name, output_file=enc_file.name)
        await my_aes.decrypt(filename=enc_file.name, output_file=dec_file.name)
        assert filecmp.cmp(in_file.name, dec_file.name) is True


@pytest.mark.parametrize("block_size", [16, 32, 48, 56])
def test_ctr_mode_string_complete(test_string, hex_key, block_size):
    if block_size != DEFAULT_BLOCK_SIZE:
        pytest.skip(f"Blocksize != 16 is not supported ({block_size})")
    my_aes = StringCounterMode(block_size=block_size, key=hex_key(block_size))
    my_aes.set_nonce(sample_nonce(block_size // 2))
    enc_text_blocks = list(my_aes.encrypt(test_string))
    dec_test = "".join(my_aes.decrypt(enc_text_blocks))
    assert dec_test == test_string


def test_ctr_mode_string_empty(hex_key):
    my_aes = StringCounterMode(key=hex_key(16), block_size=DEFAULT_BLOCK_SIZE)
    my_aes.set_nonce(sample_nonce(8))
    enc_blocks = list(my_aes.encrypt(""))
    dec = "".join(my_aes.decrypt(enc_blocks))
    assert dec == ""


def test_ctr_mode_string_single_block(hex_key):
    my_aes = StringCounterMode(key=hex_key(16), block_size=DEFAULT_BLOCK_SIZE)
    my_aes.set_nonce(sample_nonce(8))
    text = "X" * DEFAULT_BLOCK_SIZE
    enc_blocks = list(my_aes.encrypt(text))
    dec = "".join(my_aes.decrypt(enc_blocks))
    assert dec == text


def test_ctr_mode_string_non_aligned(hex_key):
    my_aes = StringCounterMode(key=hex_key(16), block_size=DEFAULT_BLOCK_SIZE)
    my_aes.set_nonce(sample_nonce(8))
    text = "Z" * (DEFAULT_BLOCK_SIZE + 1)
    enc_blocks = list(my_aes.encrypt(text))
    dec = "".join(my_aes.decrypt(enc_blocks))
    assert dec == text


async def test_ctr_mode_bytes_empty(default_hex_key, tmp_path):
    data_file = tmp_path / "empty.bin"
    data_file.write_bytes(b"")
    my_aes = ByteCounterMode(key=default_hex_key, block_size=DEFAULT_BLOCK_SIZE)
    my_aes.set_nonce(sample_nonce(8))
    enc_file = tmp_path / "enc.bin"
    dec_file = tmp_path / "dec.bin"
    await my_aes.encrypt(filename=str(data_file), output_file=str(enc_file))
    await my_aes.decrypt(filename=str(enc_file), output_file=str(dec_file))
    assert filecmp.cmp(str(data_file), str(dec_file)) is True


async def test_ctr_mode_bytes_single_block(default_hex_key, tmp_path):
    data_file = tmp_path / "single.bin"
    data_file.write_bytes(b"X" * DEFAULT_BLOCK_SIZE)
    my_aes = ByteCounterMode(key=default_hex_key, block_size=DEFAULT_BLOCK_SIZE)
    my_aes.set_nonce(sample_nonce(8))
    enc_file = tmp_path / "enc.bin"
    dec_file = tmp_path / "dec.bin"
    await my_aes.encrypt(filename=str(data_file), output_file=str(enc_file))
    await my_aes.decrypt(filename=str(enc_file), output_file=str(dec_file))
    assert filecmp.cmp(str(data_file), str(dec_file)) is True


async def test_ctr_mode_bytes_binary_data(default_hex_key, tmp_path):
    data_file = tmp_path / "binary.bin"
    data_file.write_bytes(bytes(range(256)))
    my_aes = ByteCounterMode(key=default_hex_key, block_size=DEFAULT_BLOCK_SIZE)
    my_aes.set_nonce(sample_nonce(8))
    enc_file = tmp_path / "enc.bin"
    dec_file = tmp_path / "dec.bin"
    await my_aes.encrypt(filename=str(data_file), output_file=str(enc_file))
    await my_aes.decrypt(filename=str(enc_file), output_file=str(dec_file))
    assert filecmp.cmp(str(data_file), str(dec_file)) is True
