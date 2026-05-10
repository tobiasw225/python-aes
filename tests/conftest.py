import secrets
from collections.abc import Callable

import pytest

from python_aes.aes256 import DEFAULT_BLOCK_SIZE
from python_aes.key_manager import expand_key
from python_aes.text_to_number_conversion import hex_digits_to_block


@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


@pytest.fixture(scope="module")
def test_string():
    return "Ich bin ein kleiner Test String."


@pytest.fixture()
def small_byte_file(small_txt_file_name):
    with open(small_txt_file_name) as fin:
        yield fin


@pytest.fixture(scope="session")
def small_txt_file_name():
    return "data/small.txt"


@pytest.fixture(scope="module")
def random_test_block():
    return hex_digits_to_block(secrets.token_hex(16))


@pytest.fixture(scope="module")
def hex_key() -> Callable:
    def _hex_key(n: int) -> str:
        return secrets.token_hex(n * 2)

    return _hex_key


@pytest.fixture()
def default_hex_key(hex_key):
    return hex_key(DEFAULT_BLOCK_SIZE)


@pytest.fixture(scope="module")
def key(hex_key):
    return hex_digits_to_block(hex_key(16))


@pytest.fixture(scope="module")
def expanded_key(key):
    return expand_key(key)
