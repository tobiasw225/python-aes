import os
import pytest
from python_aes.helper import get_key
from python_aes.helper import get_block

folder = "/home/tobias/mygits/python-aes/res/"


@pytest.fixture(scope="module")
def test_string():
    return "Ich bin ein kleiner Test String."


@pytest.fixture(scope="module")
def original_byte_file():
    return os.path.join(folder, 'test.jpg')


@pytest.fixture(scope="module")
def dec_byte_file():
    return os.path.join(folder, 'test.dec.jpg')


@pytest.fixture(scope="module")
def enc_byte_file():
    return os.path.join(folder, 'test.enc.jpg')


@pytest.fixture(scope="module")
def original_txt_file():
    return os.path.join(folder, 'test.txt')




@pytest.fixture(scope="module")
def key():
    return os.path.join(folder, 'testKey')


@pytest.fixture(scope="module")
def test_block():
    return get_block(os.path.join(folder, 'testBlock'))


@pytest.fixture(scope="module")
def key():
    return get_key(os.path.join(folder, 'testKey'))

