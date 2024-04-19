import filecmp
import tempfile

from python_aes.aes256 import AESBytes, AESString


def test_if_string_dec_equal_original(test_string, hex_key):
    my_aes = AESString()
    my_aes.set_key(hex_key(16))
    enc = "".join(s for s in my_aes.encrypt(test_string))
    dec_string = "".join(s for s in my_aes.decrypt(enc)).rstrip()
    assert test_string == dec_string


# def test_wiki_articles(random_wiki_articles):
#     # flaky
#     my_aes = AESString()
#     for article in random_wiki_articles:
#         enc = "".join(s for s in my_aes.encrypt(article))
#         dec_string = "".join(s for s in my_aes.decrypt(enc)).rstrip()
#         assert dec_string.strip() == article.strip()


def test_if_dec_byte_equal_original(original_byte_file, hex_key):
    my_aes = AESBytes()
    my_aes.set_key(hex_key(16))
    with original_byte_file as in_file, tempfile.NamedTemporaryFile() as enc_file, tempfile.NamedTemporaryFile() as dec_file:
        my_aes.encrypt(filename=in_file.name, output_file=enc_file.name)
        my_aes.decrypt(filename=enc_file.name, output_file=dec_file.name)
        assert filecmp.cmp(in_file.name, dec_file.name) is True
