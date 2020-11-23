import filecmp
from python_aes.aes_interface import AESString
from python_aes.aes_interface import AESBytes


def test_if_string_dec_equal_original(test_string):
    my_aes = AESString()
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


def test_if_dec_byte_equal_original(original_byte_file, dec_byte_file, enc_byte_file):
    my_aes = AESBytes()
    my_aes.encrypt(filename=original_byte_file, output_file=enc_byte_file)
    my_aes.decrypt(filename=enc_byte_file, output_file=dec_byte_file)
    assert filecmp.cmp(original_byte_file, dec_byte_file) is True
