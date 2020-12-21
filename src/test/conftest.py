import secrets
from contextlib import contextmanager

import shutil

import urllib.request

import tempfile

import pytest

from src.key_manager import expand_key
from src.util import hex_digits_to_block
from src.test.utils import get_random_wiki_articles


@pytest.fixture(scope="module")
def test_string():
    return "Ich bin ein kleiner Test String."


@contextmanager
def download_test_file_handler(url: str):
    """
    download file with url, save it to tmp-file
    and afterwards clean up.
    >>> with download_test_file_handler("https://www.w3.org/TR/PNG/iso_8859-1.txt") as file:
    ...       pass

    :param url:
    :return:
    """
    file = tempfile.NamedTemporaryFile()
    with urllib.request.urlopen(url) as response:
        shutil.copyfileobj(response, file)
    try:
        yield file
    finally:
        file.close()


@pytest.fixture(scope="module")
def original_byte_file():
    return download_test_file_handler(
        "https://upload.wikimedia.org/wikipedia/commons/f/ff/Oxygen-actions-im-qq.svg?download"
    )


@pytest.fixture(scope="module")
def original_txt_file():
    return download_test_file_handler(
        "https://archive.org/stream/goodytwoshoes00newyiala/goodytwoshoes00newyiala_djvu.txt"
    )


@pytest.fixture(scope="module")
def original_hebrew_file():
    return download_test_file_handler(
        "http://titus.uni-frankfurt.de/unicode/alphabet/hebrtest.htm"
    )


@pytest.fixture(scope="module")
def random_test_block():
    return hex_digits_to_block(secrets.token_hex(16))


@pytest.fixture(scope="module")
def hex_key() -> str:
    return secrets.token_hex(32)


@pytest.fixture(scope="module")
def key(hex_key):
    return hex_digits_to_block(hex_key)


@pytest.fixture(scope="module")
def expanded_key(key):
    return expand_key(key)


@pytest.fixture(scope="module")
def random_wiki_articles():
    return list(get_random_wiki_articles(3))
