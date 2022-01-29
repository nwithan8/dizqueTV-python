import os

from dotenv import load_dotenv

import dizqueTV


def client() -> dizqueTV.API:
    load_dotenv()
    url = os.getenv("D_URL")
    if not url:
        raise ValueError("D_URL is not set")
    return dizqueTV.API(url=url, verbose=True)
