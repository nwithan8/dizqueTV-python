import json
from datetime import datetime
from typing import List, Union

from plexapi.video import Video, Movie, Episode
from plexapi.server import PlexServer as PServer

from dizqueTV.exceptions import MissingSettingsError, NotRemoteObjectError
import dizqueTV.requests as requests


def combine_settings(new_settings_dict: json, old_settings_dict: json) -> json:
    """
    Build a complete dictionary for new settings, using old settings as a base
    :param new_settings_dict: Dictionary of new settings kwargs
    :param old_settings_dict: Current settings
    :return: Dictionary of new settings
    """
    for k, v in new_settings_dict.items():
        if k in old_settings_dict.keys():
            old_settings_dict[k] = v
    return old_settings_dict


def settings_are_complete(new_settings_dict: json, template_settings_dict: json, ignore_id: bool = False) -> bool:
    """
    Check that all elements from the settings template are present in the new settings
    :param new_settings_dict: Dictionary of new settings kwargs
    :param template_settings_dict: Template of settings
    :param ignore_id: Ignore if "_id" is not included in new_settings_dict
    :return: True if valid, raise dizqueTV.exceptions.IncompleteSettingsError if not valid
    """
    for k in template_settings_dict.keys():
        if k not in new_settings_dict.keys():
            # or not isinstance(new_settings_dict[k], type(template_settings_dict[k]))
            if k == '_id' and ignore_id:
                pass
            else:
                print(k)
                raise MissingSettingsError
    return True


def make_program_dict_from_plex_item(plex_item: Union[Video, Movie, Episode], plex_server: PServer) -> dict:
    """
    Build a dictionary for a Program using a PlexAPI Video, Movie or Episode object
    :param plex_item: plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode object
    :param plex_server: plexapi.server.PlexServer object
    :return: dict of Plex item information
    """
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
        'date': remove_time_from_date(plex_item.originallyAvailableAt),
        'year': get_year_from_date(plex_item.originallyAvailableAt),
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
    return data


def make_filler_dict_from_plex_item(plex_item: Union[Video, Movie, Episode], plex_server: PServer) -> dict:
    """
    Build a dictionary for a Filler using a PlexAPI Video, Movie or Episode object
    :param plex_item: plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode object
    :param plex_server: plexapi.server.PlexServer object
    :return: dict of Plex item information
    """
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
        'date': remove_time_from_date(plex_item.originallyAvailableAt),
        'year': get_year_from_date(plex_item.originallyAvailableAt),
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
    return data


def make_server_dict_from_plex_server(plex_server: PServer,
                                      auto_reload_channels: bool = False,
                                      auto_reload_guide: bool = True) -> dict:
    """
    Build a dictionary for a PlexServer using a PlexAPI server
    :param plex_server: plexapi.server.PlexServer object
    :param auto_reload_guide: Auto-update guide
    :param auto_reload_channels: Auto-update channels
    :return: dict of PlexServer item information
    """
    data = {
        'name': plex_server.friendlyName,
        'uri': get_plex_indirect_uri(plex_server=plex_server),
        'accessToken': get_plex_access_token(plex_server=plex_server),
        'arChannels': auto_reload_channels,
        'arGuide': auto_reload_guide
    }
    return data


def remove_time_from_date(date_string: datetime) -> str:
    """
    Remove time, i.e. 00:00:00, from a datetime.datetime string
    :param date_string: datetime.datetime object to convert
    :return: str without time, i.e. 2020-08-29
    """
    return date_string.strftime("%Y-%m-%d")


def get_year_from_date(date_string: datetime) -> int:
    """
    Extract year from a datetime.datetime string
    :param date_string: datetime.datetime object
    :return: int of year, i.e. 2020
    """
    return int(date_string.strftime("%Y"))


def get_plex_indirect_uri(plex_server: PServer) -> Union[str, None]:
    headers = {
        'Accept': 'application/json',
        'X-Plex-Product': 'dizqueTV',
        'X-Plex-Version': 'Plex OAuth',
        'X-Plex-Client-Identifier': 'rg14zekk3pa5zp4safjwaa8z',
        'X-Plex-Model': 'Plex OAuth',
        'X-Plex-Token': plex_server._token
    }
    response = requests.get(url="https://plex.tv/api/v2/resources?includeHttps=1", headers=headers)
    if response:
        json_data = response.json()
        for server in json_data:
            if server['name'] == plex_server.friendlyName:
                return server['connections'][0]['uri']
    return None


def get_plex_access_token(plex_server: PServer) -> Union[str, None]:
    headers = {
        'Accept': 'application/json',
        'X-Plex-Product': 'dizqueTV',
        'X-Plex-Version': 'Plex OAuth',
        'X-Plex-Client-Identifier': 'rg14zekk3pa5zp4safjwaa8z',
        'X-Plex-Model': 'Plex OAuth',
        'X-Plex-Token': plex_server._token
    }
    response = requests.get(url="https://plex.tv/api/v2/resources?includeHttps=1", headers=headers)
    if response:
        json_data = response.json()
        for server in json_data:
            if server['name'] == plex_server.friendlyName:
                return server['accessToken']
    return None


def check_for_dizque_instance(func):
    def inner(obj, **kwargs):
        if obj._dizque_instance:
            return func(obj, **kwargs)
        raise NotRemoteObjectError(object_type=type(obj).__name__)
    return inner
