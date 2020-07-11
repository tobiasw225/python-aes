import os
import pytest
import requests

from python_aes.helper import get_key
from python_aes.helper import get_block

folder = "/home/tobias/mygits/python-aes/res/"


@pytest.fixture(scope="module")
def test_string():
    return "Ich bin ein kleiner Test String."


@pytest.fixture(scope="module")
def original_byte_file():
    return os.path.join(folder, "test.png")


@pytest.fixture(scope="module")
def dec_byte_file():
    return os.path.join(folder, "test.dec.png")


@pytest.fixture(scope="module")
def enc_byte_file():
    return os.path.join(folder, "test.enc.png")


@pytest.fixture(scope="module")
def original_txt_file():
    return os.path.join(folder, "test.txt")


@pytest.fixture(scope="module")
def key():
    return os.path.join(folder, "testKey")


@pytest.fixture(scope="module")
def test_block():
    return get_block(os.path.join(folder, "testBlock"))


@pytest.fixture(scope="module")
def key():
    return get_key(os.path.join(folder, "testKey"))


@pytest.fixture(scope="module")
def random_wiki_articles():
    return list(get_random_wiki_articles(3))


def get_random_wiki_articles(n: int):
    """

    :param n:
    :return:
    """
    session = requests.Session()
    url = "https://en.wikipedia.org/w/api.php"
    res = session.get(
        url=url,
        params={
            "action": "query",
            "format": "json",
            "list": "random",
            "rnlimit": f"{n}",
        },
    )
    data = res.json()
    articles = data["query"]["random"]
    # crawl actual articles
    res = session.get(
        url=url,
        params={
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exlimit": "max",
            "explaintext": "true",
            "titles": "|".join(r["title"] for r in articles),
        },
    )
    data = res.json()
    for article in data["query"]["pages"].values():
        # some articles have no text.
        yield f"{article['title']}\n{article.get('extract', '')}"
