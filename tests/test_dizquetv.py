from time import sleep

import pytest

import dizqueTV
from tests.setup import (client,
                         fake_plex_server,
                         plex_server,
                         _plex_vars_exist,
                         plex_server_as_dizquetv_server)

REAL_PLEX_SERVER_ADDED = False


def use_real_plex():
    if not client().get_plex_server(plex_server().friendlyName):
        yield client().add_plex_server_from_plexapi(plex_server())
    else:
        yield client().get_plex_server(plex_server().friendlyName)


def should_use_real_plex() -> bool:
    return _plex_vars_exist()


class TestGeneral:
    def test_dizquetv_server_details(self):
        details = client().dizquetv_server_details
        assert details.server_version != ""
        assert details.ffmpeg_version != ""
        assert details.nodejs_version != ""

    def test_dizquetv_version(self):
        version = client().dizquetv_version
        assert version != ""

    def test_ffmpeg_version(self):
        version = client().ffmpeg_version
        assert version != ""

    def test_nodejs_version(self):
        version = client().nodejs_version
        assert version != ""

    def test_ffmpeg_settings(self):
        settings = client().ffmpeg_settings
        assert settings is not None
        assert settings.configVersion != ""

    def test_plex_settings(self):
        settings = client().plex_settings
        assert settings is not None
        assert settings.transcodeBitrate != ""

    def test_xmltv_settings(self):
        settings = client().xmltv_settings
        assert settings is not None
        assert settings.file != ""

    def test_hdhr_settings(self):
        settings = client().hdhr_settings
        assert settings is not None
        assert settings.tunerCount != ""

    def test_channel_count(self):
        count = client().channel_count
        assert type(count) == int

    def test_channel_list(self):
        channels = client().channels
        assert type(channels) == list

    def test_channel_programs_property(self):
        channels = client().channels
        for channel in channels:
            programs = channel.programs
            assert type(programs) == list

    def test_channel_programs_method(self):
        channels = client().channels
        for channel in channels:
            programs = client().get_channel_programs(channel_number=channel.number)
            assert type(programs) == list


class TestWithFakePlex:
    def test_add_plex_server(self):
        # add a fake Plex server
        server = client().get_plex_server(server_name=fake_plex_server["name"])
        assert server is None
        server = client().add_plex_server(**fake_plex_server)
        assert type(server) == dizqueTV.PlexServer

    def test_plex_servers(self):
        servers = client().plex_servers
        assert type(servers) == list

    def test_plex_server_status(self):
        status = client().plex_server_status(server_name=fake_plex_server["name"])
        assert type(status) == bool

    def test_plex_server_foreign_status(self):
        status = client().plex_server_foreign_status(
            server_name=fake_plex_server["name"]
        )
        assert type(status) == bool

    def test_get_plex_server(self):
        server = client().get_plex_server(server_name=fake_plex_server["name"])
        assert type(server) in [dizqueTV.PlexServer, None]

    def test_update_plex_server(self):
        server = client().get_plex_server(server_name=fake_plex_server["name"])
        assert server.arGuide is False
        success = client().update_plex_server(
            server_name=fake_plex_server["name"], arGuide=True
        )
        # request/update is successful, but throwing a timeout error, so success is False
        server = client().get_plex_server(server_name=fake_plex_server["name"])
        assert server.arGuide is True

    def test_delete_plex_server(self):
        server = client().get_plex_server(server_name=fake_plex_server["name"])
        assert server is not None
        success = client().delete_plex_server(server_name=fake_plex_server["name"])
        # request/update is successful, but throwing a timeout error, so success is False
        sleep(1)
        server = client().get_plex_server(server_name=fake_plex_server["name"])
        assert server is None


class TestWithRealPlex:
    def test_use_real_plex(self):
        if not should_use_real_plex():
            pytest.skip("No real Plex server found")
        server = use_real_plex
        assert server is not None
        assert type(server) == dizqueTV.PlexServer
        assert server.name == plex_server().friendlyName
