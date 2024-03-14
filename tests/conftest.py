import secrets
import shutil
import tempfile
import urllib.request
from collections.abc import Callable
from contextlib import contextmanager
from tests.utils_test import get_random_wiki_articles, random_utf_word

import pytest

from base.key_manager import expand_key
from base.text_to_number_conversion import hex_digits_to_block


@pytest.fixture(scope="module")
def test_string():
    return "Ich bin ein kleiner Test String."


@pytest.fixture(scope="module")
def test_utf_8_text():
    return " ".join(random_utf_word(k=i) for i in range(100))


@pytest.fixture(scope="module")
def original_byte_file():
    with open("tests/data/goodytwoshoes00newyiala_djvu.txt") as fin:
        yield fin


@pytest.fixture(scope="module")
def original_txt_file():
    with open("tests/data/goodytwoshoes00newyiala_djvu.txt") as fin:
        yield fin


@pytest.fixture(scope="module")
def original_hebrew_file():
    with open("tests/data/hebrtest.htm") as fin:
        yield fin


@pytest.fixture(scope="module")
def random_test_block():
    return hex_digits_to_block(secrets.token_hex(16))


@pytest.fixture(scope="module")
def hex_key() -> Callable:
    def _hex_key(n: int) -> str:
        return secrets.token_hex(n*2)
    return _hex_key


@pytest.fixture(scope="module")
def key(hex_key):
    return hex_digits_to_block(hex_key(16))


@pytest.fixture(scope="module")
def expanded_key(key):
    return expand_key(key)


@pytest.fixture(scope="module")
def random_wiki_articles():
    return list(get_random_wiki_articles(3))
