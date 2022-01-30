import os

from dotenv import load_dotenv

import dizqueTV
import plexapi

fake_plex_server = {
    'name': 'Test',
    'uri': 'http://localhost:32400',
    'accessToken': '12345',
    'index': 0,
    'arChannels': False,
    'arGuide': False,
    '_id': 'myid',
}


def client() -> dizqueTV.API:
    load_dotenv()
    url = os.getenv("D_URL")
    if not url:
        raise ValueError("D_URL is not set")
    return dizqueTV.API(url=url, verbose=True)


def _make_plex_utils() -> dizqueTV.PlexUtils:
    load_dotenv()
    url = os.getenv("PLEX_URL")
    if not url:
        raise ValueError("PLEX_URL is not set")
    token = os.getenv("PLEX_TOKEN")
    if not token:
        raise ValueError("PLEX_TOKEN is not set")
    return dizqueTV.PlexUtils(url=url, token=token)


def plex_server() -> 'plexapi.server.PlexServer':
    utils = _make_plex_utils()
    return utils.server


def plex_server_as_dizquetv_server() -> dizqueTV.PlexServer:
    utils = _make_plex_utils()
    return utils.as_dizquetv_plex_server
