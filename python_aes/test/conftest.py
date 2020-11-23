import pytest

from python_aes.helper import get_key
from python_aes.helper import get_block
from python_aes.test.utils import download
from python_aes.test.utils import get_random_wiki_articles


@pytest.fixture(scope="module")
def test_string():
    return "Ich bin ein kleiner Test String."


@pytest.fixture(scope="module")
def original_byte_file():
    filename = "test.svg"
    url = "https://upload.wikimedia.org/wikipedia/commons/f/ff/Oxygen-actions-im-qq.svg?download"
    download(url=url, output_file=filename)
    return filename


@pytest.fixture(scope="module")
def dec_byte_file():
    return "test.dec.svg"


@pytest.fixture(scope="module")
def enc_byte_file():
    return "test.enc.svg"


@pytest.fixture(scope="module")
def original_txt_file():
    filename = "test.txt"
    url = "https://archive.org/stream/goodytwoshoes00newyiala/goodytwoshoes00newyiala_djvu.txt"
    download(url=url, output_file=filename)
    return filename


@pytest.fixture(scope="module")
def original_hebrew_file():
    filename = "test_hebrew.txt"
    url = "http://titus.uni-frankfurt.de/unicode/alphabet/hebrtest.htm"
    download(url=url, output_file=filename)
    return filename


@pytest.fixture(scope="module")
def test_block():
    return get_block("00112233445566778899aabbccddeeff")


@pytest.fixture(scope="module")
def key():
    return get_key("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")


@pytest.fixture(scope="module")
def random_wiki_articles():
    return list(get_random_wiki_articles(3))