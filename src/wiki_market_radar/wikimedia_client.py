from urllib.parse import quote

import requests

BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"

HEADERS = {
    "User-Agent": (
        "wiki-market-radar/0.1 "
        "(https://github.com/wiki-signal/wiki-market-radar)"
    )
}


def fetch_pageviews(
    project: str,
    article: str,
    start: str,
    end: str,
    granularity: str = "daily",
) -> list[dict]:
    encoded_article = quote(article.replace(" ", "_"), safe="")

    url = (
        f"{BASE_URL}/"
        f"{project}/all-access/user/"
        f"{encoded_article}/{granularity}/{start}/{end}"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data["items"]