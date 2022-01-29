from time import sleep

import dizqueTV
from tests.setup import client, plex_server, plex_server_as_dizquetv_server, fake_plex_server


def test_dizquetv_server_details():
    details = client().dizquetv_server_details
    assert details.server_version != ''
    assert details.ffmpeg_version != ''
    assert details.nodejs_version != ''


def test_dizquetv_version():
    version = client().dizquetv_version
    assert version != ''


def test_ffmpeg_version():
    version = client().ffmpeg_version
    assert version != ''


def test_nodejs_version():
    version = client().nodejs_version
    assert version != ''


def test_ffmpeg_settings():
    settings = client().ffmpeg_settings
    assert settings is not None
    assert settings.configVersion != ''


def test_plex_settings():
    settings = client().plex_settings
    assert settings is not None
    assert settings.transcodeBitrate != ''


def test_xmltv_settings():
    settings = client().xmltv_settings
    assert settings is not None
    assert settings.file != ''


def test_hdhr_settings():
    settings = client().hdhr_settings
    assert settings is not None
    assert settings.tunerCount != ''


def test_add_plex_server():
    server = client().get_plex_server(server_name=fake_plex_server['name'])
    assert server is None
    server = client().add_plex_server(**fake_plex_server)
    assert type(server) == dizqueTV.PlexServer


def test_plex_servers():
    servers = client().plex_servers
    assert type(servers) == list


def test_plex_server_status():
    status = client().plex_server_status(server_name=fake_plex_server['name'])
    assert type(status) == bool


def test_plex_server_foreign_status():
    status = client().plex_server_foreign_status(server_name=fake_plex_server['name'])
    assert type(status) == bool


def test_get_plex_server():
    server = client().get_plex_server(server_name=fake_plex_server['name'])
    assert type(server) in [dizqueTV.PlexServer, None]


def test_update_plex_server():
    server = client().get_plex_server(server_name=fake_plex_server['name'])
    assert server.arGuide is False
    success = client().update_plex_server(server_name=fake_plex_server['name'], arGuide=True)
    # request/update is successful, but throwing a timeout error, so success is False
    server = client().get_plex_server(server_name=fake_plex_server['name'])
    assert server.arGuide is True


def test_delete_plex_server():
    server = client().get_plex_server(server_name=fake_plex_server['name'])
    assert server is not None
    success = client().delete_plex_server(server_name=fake_plex_server['name'])
    # request/update is successful, but throwing a timeout error, so success is False
    sleep(1)
    server = client().get_plex_server(server_name=fake_plex_server['name'])
    assert server is None
