import requests


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
