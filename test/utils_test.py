import random
from typing import Iterable, List

import requests

from utils import generate_nonce


def assert_blocks_equal(block_a: Iterable, block_b: Iterable):
    for a, b in zip(block_a, block_b):
        assert a == b


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


def sample_nonce(block_size: int) -> List[int]:
    nonce = [0] * block_size
    _nonce = generate_nonce(d_type="int", block_size=block_size // 2)
    for i, n in enumerate(_nonce):
        nonce[i] = n
    return nonce


def random_utf_word(k: int) -> str:
    return "".join(
        random.choices(
            tuple(chr(i) for i in range(32, 100000) if chr(i).isprintable()), k=k
        )
    )
