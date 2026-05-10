import filecmp
import tempfile

import aiofiles

from python_aes.aes256 import AESBytesCBC, AESString, AESBytesECB


async def test_if_string_dec_equal_original(test_string, default_hex_key):
    my_aes = AESString(key=default_hex_key)
    enc_blocks = my_aes.encrypt(test_string)
    enc = "".join(s for s in enc_blocks)
    dec_string = "".join(s for s in my_aes.decrypt(enc))
    assert test_string == dec_string


async def test_cbc_if_dec_byte_equal_original(small_txt_file_name, default_hex_key):
    my_aes = AESBytesCBC(key=default_hex_key)
    async with aiofiles.open(small_txt_file_name) as in_file:
        with tempfile.NamedTemporaryFile() as enc_file, tempfile.NamedTemporaryFile() as dec_file:
            await my_aes.encrypt(filename=in_file.name, output_file=enc_file.name)
            await my_aes.decrypt(filename=enc_file.name, output_file=dec_file.name)
            assert filecmp.cmp(in_file.name, dec_file.name) is True


async def test_ecb_if_dec_byte_equal_original(
    original_byte_file, default_hex_key, small_txt_file_name
):
    my_aes = AESBytesECB(key=default_hex_key)
    async with aiofiles.open(small_txt_file_name) as in_file:
        with tempfile.NamedTemporaryFile() as enc_file, tempfile.NamedTemporaryFile() as dec_file:
            await my_aes.encrypt(filename=in_file.name, output_file=enc_file.name)
            await my_aes.decrypt(filename=enc_file.name, output_file=dec_file.name)
            assert filecmp.cmp(in_file.name, dec_file.name) is True
