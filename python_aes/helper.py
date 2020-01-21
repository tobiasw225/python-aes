#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: helper.py
#
# __description__:
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel

import random
import os
import re
import numpy as np


def print_block(block: list):
    """

    :param block:
    :return:
    """
    for i in range(0, 16, 4):
        print("\t".join(block[i:i+4]))
        print("\n")


def rand_key() -> str:
    """

    :return:
    """
    rk = np.random.randint(0, 255, 32)
    rk = [format(i,  '02x') for i in rk]
    return "".join(rk)


def fmap(x):
    """

    :param x:
    :return:
    """
    return int(x, 16)


def process_block(block: str) -> np.ndarray:
    """

    :param block:
    :return:
    """
    block = re.findall('..', block)  # splits the string in 2pairs
    return np.array(list(map(fmap, block)), dtype=int)


def get_key(key: str) -> np.ndarray:
    """

    :param key:
    :return:
    """
    if os.path.isfile(key):
        with open(key, "r") as f:
            key = f.read()
    return np.array(process_block(key))



get_block = get_key


def chunks(blocks, n: int = 16):
    """
        Yield successive n-sized chunks from blocks.

    :param blocks:
    :param n:
    :return:
    """
    for i in range(0, len(blocks), n):
        yield blocks[i:i + n]


"""
    get_random.py

    MediaWiki API Demos
    Demo of `Random` module: Get request to list 5 random pages.

    MIT License
"""


import requests


def get_random_wiki_articles(n: int):
    """

    :param n:
    :return:
    """
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnlimit": f"{n}"
    }
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    RANDOMS = DATA["query"]["random"]
    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exlimit": "max",
        "explaintext": "true",
        "titles": "|".join(r['title'] for r in RANDOMS)
    }
    # crawl actual articles
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    for article in DATA['query']['pages'].values():
        # some articles have no text.
        yield f"{article['title']}\n{article.get('extract', '')}"

