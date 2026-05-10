import filecmp
import tempfile

import aiofiles

from python_aes.aes256 import AESBytesCBC, AESBytesECB, AESString


async def test_if_string_dec_equal_original(test_string, default_hex_key):
    my_aes = AESString(key=default_hex_key)
    enc_blocks = my_aes.encrypt(test_string)
    enc = "".join(s for s in enc_blocks)
    dec_string = "".join(s for s in my_aes.decrypt(enc))
    assert test_string == dec_string


async def test_cbc_if_dec_byte_equal_original(small_txt_file_name, default_hex_key):
    my_aes = AESBytesCBC(key=default_hex_key)
    async with aiofiles.open(small_txt_file_name) as in_file:
        with (
            tempfile.NamedTemporaryFile() as enc_file,
            tempfile.NamedTemporaryFile() as dec_file,
        ):  # noqa: E501
            await my_aes.encrypt(filename=in_file.name, output_file=enc_file.name)
            await my_aes.decrypt(filename=enc_file.name, output_file=dec_file.name)
            assert filecmp.cmp(in_file.name, dec_file.name) is True


async def test_ecb_if_dec_byte_equal_original(default_hex_key, small_txt_file_name):
    my_aes = AESBytesECB(key=default_hex_key)
    async with aiofiles.open(small_txt_file_name) as in_file:
        with (
            tempfile.NamedTemporaryFile() as enc_file,
            tempfile.NamedTemporaryFile() as dec_file,
        ):  # noqa: E501
            await my_aes.encrypt(filename=in_file.name, output_file=enc_file.name)
            await my_aes.decrypt(filename=enc_file.name, output_file=dec_file.name)
            assert filecmp.cmp(in_file.name, dec_file.name) is True


async def test_aes_string_empty_string(default_hex_key):
    my_aes = AESString(key=default_hex_key)
    enc = "".join(my_aes.encrypt(""))
    dec_string = "".join(my_aes.decrypt(enc))
    assert dec_string == ""


async def test_aes_string_single_block(default_hex_key):
    my_aes = AESString(key=default_hex_key)
    text = "A" * my_aes.block_size
    enc = "".join(my_aes.encrypt(text))
    dec_string = "".join(my_aes.decrypt(enc))
    assert dec_string == text


async def test_aes_string_non_aligned(default_hex_key):
    my_aes = AESString(key=default_hex_key)
    text = "B" * (my_aes.block_size + 1)
    enc = "".join(my_aes.encrypt(text))
    dec_string = "".join(my_aes.decrypt(enc))
    assert dec_string == text


async def test_aes_bytes_ecb_empty_file(default_hex_key, tmp_path):
    data_file = tmp_path / "empty.txt"
    data_file.write_text("")
    my_aes = AESBytesECB(key=default_hex_key)
    enc_file = tmp_path / "enc.bin"
    dec_file = tmp_path / "dec.bin"
    await my_aes.encrypt(filename=str(data_file), output_file=str(enc_file))
    await my_aes.decrypt(filename=str(enc_file), output_file=str(dec_file))
    assert filecmp.cmp(str(data_file), str(dec_file)) is True


async def test_aes_bytes_ecb_single_block(default_hex_key, tmp_path):
    data_file = tmp_path / "single_block.txt"
    data_file.write_bytes(b"A" * 16)
    my_aes = AESBytesECB(key=default_hex_key)
    enc_file = tmp_path / "enc.bin"
    dec_file = tmp_path / "dec.bin"
    await my_aes.encrypt(filename=str(data_file), output_file=str(enc_file))
    await my_aes.decrypt(filename=str(enc_file), output_file=str(dec_file))
    assert filecmp.cmp(str(data_file), str(dec_file)) is True


async def test_aes_bytes_cbc_empty_file(default_hex_key, tmp_path):
    data_file = tmp_path / "empty.txt"
    data_file.write_text("")
    my_aes = AESBytesCBC(key=default_hex_key)
    enc_file = tmp_path / "enc.bin"
    dec_file = tmp_path / "dec.bin"
    await my_aes.encrypt(filename=str(data_file), output_file=str(enc_file))
    await my_aes.decrypt(filename=str(enc_file), output_file=str(dec_file))
    assert filecmp.cmp(str(data_file), str(dec_file)) is True


async def test_aes_bytes_cbc_single_block(default_hex_key, tmp_path):
    data_file = tmp_path / "single_block.txt"
    data_file.write_bytes(b"B" * 16)
    my_aes = AESBytesCBC(key=default_hex_key)
    enc_file = tmp_path / "enc.bin"
    dec_file = tmp_path / "dec.bin"
    await my_aes.encrypt(filename=str(data_file), output_file=str(enc_file))
    await my_aes.decrypt(filename=str(enc_file), output_file=str(dec_file))
    assert filecmp.cmp(str(data_file), str(dec_file)) is True
