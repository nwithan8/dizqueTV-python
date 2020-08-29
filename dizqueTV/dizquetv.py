import json
from urllib.parse import urlencode
from xml.etree import ElementTree
from typing import List, Union

import m3u8
import requests
from plexapi.video import Video, Movie, Episode
from plexapi.server import PlexServer as PServer

import dizqueTV.logging
from logging import info, error, warning
from dizqueTV.settings import XMLTVSettings, PlexSettings, FFMPEGSettings, HDHomeRunSettings
from dizqueTV.channels import Channel, Program
from dizqueTV.plex_server import PlexServer
from dizqueTV.templates import PLEX_SETTINGS_TEMPLATE, CHANNEL_SETTINGS_TEMPLATE
import dizqueTV.helpers as helpers


def convert_to_program(plex_item: Union[Video, Movie, Episode], plex_server: PServer) -> Program:
    item_type = plex_item.type
    plex_media_item_part = plex_item.media[0].parts[0]
    data = {
        'title': plex_item.title,
        'key': plex_item.key,
        'ratingKey': plex_item.ratingKey,
        'icon': plex_item.thumb,
        'type': item_type,
        'duration': plex_item.duration,
        'summary': plex_item.summary,
        'rating': plex_item.contentRating,
        'date': helpers.remove_time_from_date(plex_item.originallyAvailableAt),
        'year': helpers.get_year_from_date(plex_item.originallyAvailableAt),
        'plexFile': plex_media_item_part.key,
        'file': plex_media_item_part.file,
        'showTitle': (plex_item.grandparentTitle if item_type == 'episode' else plex_item.title),
        'episode': (plex_item.index if item_type == 'episode' else 1),
        'season': (plex_item.parentIndex if item_type == 'episode' else 1),
        'serverKey': plex_server.friendlyName
    }
    if plex_item.type == 'episode':
        data['episodeIcon'] = plex_item.thumb
        data['seasonIcon'] = plex_item.parentThumb
        data['showIcon'] = plex_item.grandparentThumb
    return Program(data=data, dizque_instance=None, channel_instance=None)


class API:
    def __init__(self, url: str, verbose: bool = False):
        self.url = url.rstrip('/')
        self.verbose = verbose

    def _log(self, message: str, level: Union[info, error, warning] = info) -> None:
        """
        Log a message if verbose is enabled.
        :param message: Message to log
        :param level: info, error or warning
        """
        if self.verbose:
            level(message)

    def _get(self, endpoint, params=None, timeout: int = 2) -> Union[requests.Response, None]:
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        url = f"{self.url}/api{endpoint}"
        if params:
            url += f"?{urlencode(params)}"
        self._log(message=f"GET {url}", level=info)
        try:
            return requests.get(url=url, timeout=timeout)
        except requests.exceptions.Timeout:
            return None

    def _post(self, endpoint, params=None, data=None, timeout: int = 2) -> Union[requests.Response, None]:
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        url = f"{self.url}/api{endpoint}"
        if params:
            url += f"?{urlencode(params)}"
        self._log(message=f"POST {url}, Body: {data}", level=info)
        try:
            return requests.post(url=url, json=data, timeout=timeout)
            # use json= rather than data= to convert single-quoted dict to double-quoted JSON
        except requests.exceptions.Timeout:
            return None

    def _put(self, endpoint, params=None, data=None, timeout: int = 2) -> Union[requests.Response, None]:
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        url = f"{self.url}/api{endpoint}"
        if params:
            url += f"?{urlencode(params)}"
        self._log(message=f"PUT {url}, Body: {data}", level=info)
        try:
            return requests.put(url=url, json=data, timeout=timeout)
            # use json= rather than data= to convert single-quoted dict to double-quoted JSON
        except requests.exceptions.Timeout:
            return None

    def _delete(self, endpoint, params=None, data=None, timeout: int = 2) -> Union[requests.Response, None]:
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        url = f"{self.url}/api{endpoint}"
        if params:
            url += f"?{urlencode(params)}"
        self._log(message=f"DELETE {url}", level=info)
        try:
            return requests.delete(url=url, json=data, timeout=timeout)
            # use json= rather than data= to convert single-quoted dict to double-quoted JSON
        except requests.exceptions.Timeout:
            return None

    def _get_json(self, endpoint, params=None, timeout: int = 2) -> json:
        response = self._get(endpoint=endpoint, params=params, timeout=timeout)
        if response:
            return response.json()
        return {}

    # Versions
    @property
    def dizquetv_version(self) -> str:
        """
        Get dizqueTV version number
        :return: dizqueTV version number
        """
        return self._get_json(endpoint='/version').get('dizquetv')

    @property
    def ffmpeg_version(self) -> str:
        """
        Get FFMPEG version number
        :return: ffmpeg version number
        """
        return self._get_json(endpoint='/version').get('ffmpeg')

    # Plex Servers
    @property
    def plex_servers(self) -> List[PlexServer]:
        """
        Get the Plex Media Servers connected to dizqueTV
        :return: List of PlexServer objects
        """
        json_data = self._get_json(endpoint='/plex-servers')
        return [PlexServer(data=server, dizque_instance=self) for server in json_data]

    def plex_server_status(self, server_name: str) -> bool:
        """
        Check if a Plex Media Server is accessible
        :param server_name: Name of Plex Server
        :return: True if active, False if not active
        """
        if self._post(endpoint='/plex-servers/status', data={'name': server_name}):
            return True
        return False

    def plex_server_foreign_status(self, server_name: str) -> bool:
        """

        :param server_name: Name of Plex Server
        :return: True if active, False if not active
        """
        if self._post(endpoint='/plex-servers/foreignstatus', data={'name': server_name}):
            return True
        return False

    def get_plex_server(self, server_name: str) -> Union[PlexServer, None]:
        """
        Get a specific Plex Media Server
        :param server_name: Name of Plex Server
        :return: PlexServer object or None
        """
        for server in self.plex_servers:
            if server.name == server_name:
                return server
        return None

    def add_plex_server(self, **kwargs) -> Union[PlexServer, None]:
        """
        Add a Plex Media Server to dizqueTV
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        if helpers.settings_are_complete(new_settings_dict=kwargs,
                                         template_settings_dict=PLEX_SETTINGS_TEMPLATE,
                                         ignore_id=True) \
                and self._put(endpoint='/plex-servers', data=kwargs):
            return self.get_plex_server(server_name=kwargs['name'])
        return None

    def update_plex_server(self, server_name: str, **kwargs) -> bool:
        """
        Edit a Plex Media Server on dizqueTV
        :param server_name: name of Plex Media Server to update
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        server = self.get_plex_server(server_name=server_name)
        if server:
            old_settings = server._data
            new_settings = helpers.combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
            if self._post(endpoint='/plex-servers', data=new_settings):
                return True
        return False

    def delete_plex_server(self, server_name: str) -> bool:
        """
        Remove a Plex Media Server from dizqueTV
        :param server_name: Name of Plex Server
        :return: True if successful, False if unsuccessful
        """
        if self._delete(endpoint='/plex-servers', data={'name': server_name}):
            return True
        return False

    # Channels
    @property
    def channels(self) -> List[Channel]:
        """
        Get all dizqueTV channels
        :return: List of Channel objects
        """
        json_data = self._get_json(endpoint='/channels', timeout=5)  # large JSON may take longer, so bigger timeout
        return [Channel(data=channel, dizque_instance=self) for channel in json_data]

    def get_channel(self, channel_number: int) -> Union[Channel, None]:
        """
        Get a specific dizqueTV channel
        :param channel_number: Number of channel
        :return: Channel object or None
        """
        channel_data = self._get_json(endpoint=f'/channel/{channel_number}')
        if channel_data:
            return Channel(data=channel_data, dizque_instance=self)
        return None

    def get_channel_info(self, channel_number: int) -> json:
        """
        Get the name, number and icon for a dizqueTV channel
        :param channel_number: Number of channel
        :return: JSON data with channel name, number and icon path
        """
        return self._get_json(endpoint=f'/channel/description/{channel_number}')

    @property
    def channel_numbers(self) -> List[int]:
        """
        Get all dizqueTV channel numbers
        :return: List of channel numbers
        """
        data = self._get_json(endpoint='/channelNumbers')
        if data:
            return data
        return []

    def add_channel(self, **kwargs) -> Union[Channel, None]:
        """
        Add a channel to dizqueTV
        :param kwargs: keyword arguments of setting names and values
        :return: new Channel object or None
        """
        if helpers.settings_are_complete(new_settings_dict=kwargs,
                                         template_settings_dict=CHANNEL_SETTINGS_TEMPLATE,
                                         ignore_id=True) \
                and self._put(endpoint="/channel", data=kwargs):
            return self.get_channel(channel_number=kwargs['number'])
        return None

    def update_channel(self, channel_number: int, **kwargs) -> bool:
        """
        Edit a dizqueTV channel
        :param channel_number: Number of channel to update
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        channel = self.get_channel(channel_number=channel_number)
        if channel:
            old_settings = channel._data
            new_settings = helpers.combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
            if self._post(endpoint="/channel", data=new_settings):
                return True
        return False

    def delete_channel(self, channel_number: int) -> bool:
        """
        Delete a dizqueTV channel
        :return: True if successful, False if unsuccessful
        """
        if self._delete(endpoint="/channel", data={'number': channel_number}):
            return True
        return False

    # FFMPEG Settings
    @property
    def ffmpeg_settings(self) -> Union[FFMPEGSettings, None]:
        """
        Get dizqueTV's FFMPEG settings
        :return: FFMPEGSettings object or None
        """
        json_data = self._get_json(endpoint='/ffmpeg-settings')
        if json_data:
            return FFMPEGSettings(data=json_data, dizque_instance=self)
        return None

    def update_ffmpeg_settings(self, **kwargs) -> bool:
        """
        Edit dizqueTV's FFMPEG settings
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.ffmpeg_settings._data
        new_settings = helpers.combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
        if self._put(endpoint='/ffmpeg-settings', data=new_settings):
            return True
        return False

    def reset_ffmpeg_settings(self) -> bool:
        """
        Reset dizqueTV's FFMPEG settings to default
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.ffmpeg_settings._data
        if self._post(endpoint='/ffmpeg-settings', data={'_id': old_settings['_id']}):
            return True
        return False

    # Plex settings
    @property
    def plex_settings(self) -> Union[PlexSettings, None]:
        """
        Get dizqueTV's Plex settings
        :return: PlexSettings object or None
        """
        json_data = self._get_json(endpoint='/plex-settings')
        if json_data:
            return PlexSettings(data=json_data, dizque_instance=self)
        return None

    def update_plex_settings(self, **kwargs) -> bool:
        """
        Edit dizqueTV's Plex settings
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.plex_settings._data
        new_settings = helpers.combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
        if self._put(endpoint='/plex-settings', data=new_settings):
            return True
        return False

    def reset_plex_settings(self) -> bool:
        """
        Reset dizqueTV's Plex settings to default
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.plex_settings._data
        if self._post(endpoint='/plex-settings', data={'_id': old_settings['_id']}):
            return True
        return False

    # XML Refresh Time
    @property
    def last_xmltv_refresh(self) -> str:
        """
        Get the last time the XMLTV file was refreshed
        :return: Timestamp of last refresh
        """
        return self._get_json(endpoint='/xmltv-last-refresh')

    # XMLTV Settings
    @property
    def xmltv_settings(self) -> Union[XMLTVSettings, None]:
        """
        Get dizqueTV's XMLTV settings
        :return: XMLTVSettings object or None
        """
        json_data = self._get_json(endpoint='/xmltv-settings')
        if json_data:
            return XMLTVSettings(data=json_data, dizque_instance=self)
        return None

    def update_xmltv_settings(self, **kwargs) -> bool:
        """
        Edit dizqueTV's XMLTV settings
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.xmltv_settings._data
        new_settings = helpers.combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
        if self._put(endpoint='/xmltv-settings', data=new_settings):
            return True
        return False

    def reset_xmltv_settings(self) -> bool:
        """
        Reset dizqueTV's XMLTV settings to default
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.xmltv_settings._data
        if self._post(endpoint='/xmltv-settings', data={'_id': old_settings['_id']}):
            return True
        return False

    # HDHomeRun Settings
    @property
    def hdhr_settings(self) -> Union[HDHomeRunSettings, None]:
        """
        Get dizqueTV's HDHomeRun settings
        :return: HDHomeRunSettings object or None
        """
        json_data = self._get_json(endpoint='/hdhr-settings')
        if json_data:
            return HDHomeRunSettings(data=json_data, dizque_instance=self)
        return None

    def update_hdhr_settings(self, **kwargs) -> bool:
        """
        Edit dizqueTV's HDHomeRun settings
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.hdhr_settings._data
        new_settings = helpers.combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
        if self._put(endpoint='/hdhr-settings', data=new_settings):
            return True
        return False

    def reset_hdhr_settings(self) -> bool:
        """
        Reset dizqueTV's HDHomeRun settings to default
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.hdhr_settings._data
        if self._post(endpoint='/hdhr-settings', data={'_id': old_settings['_id']}):
            return True
        return False

    # XMLTV.XML
    @property
    def xmltv_xml(self) -> Union[ElementTree.Element, None]:
        """
        Get dizqueTV's XMLTV data
        :return: xml.etree.ElementTree.Element object or None
        """
        response = self._get(endpoint='/xmltv.xml')
        if response:
            return ElementTree.fromstring(response.content)
        return None

    @property
    def m3u(self) -> m3u8:
        """
        Get dizqueTV's m3u playlist
        Without m3u8, this method currently produces an error.
        :return: m3u8 object
        """
        return m3u8.load(f"{self.url}/api/channels.m3u")
