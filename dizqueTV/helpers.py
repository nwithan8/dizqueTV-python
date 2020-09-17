import json
from datetime import datetime, timedelta
from typing import List, Union, Tuple
import collections
import random

from plexapi.video import Video, Movie, Episode
from plexapi.server import PlexServer as PServer

from dizqueTV.exceptions import MissingSettingsError, NotRemoteObjectError
import dizqueTV.requests as requests

_access_tokens = {}
_uris = {}


# Checks
def _check_for_dizque_instance(func):
    """
    Check if an object has a _dizque_instance attribute before executing function
    :param func: Function to execute if object does have a _dizque_instance attribute
    :return: Result of func
    """

    def inner(obj, **kwargs):
        if obj._dizque_instance:
            return func(obj, **kwargs)
        raise NotRemoteObjectError(object_type=type(obj).__name__)

    return inner


# Internal Helpers
def _combine_settings(new_settings_dict: json, old_settings_dict: json) -> json:
    """
    Build a complete dictionary for new settings, using old settings as a base
    :param new_settings_dict: Dictionary of new settings kwargs
    :param old_settings_dict: Current settings
    :return: Dictionary of new settings
    """
    for k, v in new_settings_dict.items():
        old_settings_dict[k] = v
    return old_settings_dict


def _settings_are_complete(new_settings_dict: json, template_settings_dict: json, ignore_id: bool = False) -> bool:
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
                raise MissingSettingsError(f"Missing setting: {k}")
    return True


def _object_has_attribute(object, attribute_name: str) -> bool:
    """
    Check if an object has an attribute (exists and is not None)
    :param object: object to check
    :param attribute_name: name of attribute to find
    :return: True if exists and is not None, False otherwise
    """
    if hasattr(object, attribute_name):
        if getattr(object, attribute_name) is not None:
            return True
    return False


def _make_program_dict_from_plex_item(plex_item: Union[Video, Movie, Episode], plex_server: PServer) -> dict:
    """
    Build a dictionary for a Program using a PlexAPI Video, Movie or Episode object
    :param plex_item: plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode object
    :param plex_server: plexapi.server.PlexServer object
    :return: dict of Plex item information
    """
    item_type = plex_item.type
    plex_media_item_part = plex_item.media[0].parts[0]
    plex_uri = get_plex_indirect_uri(plex_server=plex_server)
    plex_token = get_plex_access_token(plex_server=plex_server)
    data = {
        'title': plex_item.title,
        'key': plex_item.key,
        'ratingKey': plex_item.ratingKey,
        'icon': f"{plex_uri}{plex_item.thumb}?X-Plex-Token={plex_token}",
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
        data['episodeIcon'] = f"{plex_uri}{plex_item.thumb}?X-Plex-Token={plex_token}"
        data['seasonIcon'] = f"{plex_uri}{plex_item.parentThumb}?X-Plex-Token={plex_token}"
        data['showIcon'] = f"{plex_uri}{plex_item.grandparentThumb}?X-Plex-Token={plex_token}"
    return data


def _make_filler_dict_from_plex_item(plex_item: Union[Video, Movie, Episode], plex_server: PServer) -> dict:
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


def _make_server_dict_from_plex_server(plex_server: PServer,
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


def _separate_with_and_without(items: List, attribute_name: str) -> Tuple[List, List]:
    """
    Split a list of items into those with a specific attribute and those without
    :param items: List of items
    :param attribute_name: Name of attribute to look for
    :return: list_with, list_without
    """
    items_with = []
    items_without = []
    for item in items:
        if _object_has_attribute(object=item, attribute_name=attribute_name):
            items_with.append(item)
        else:
            items_without.append(item)
    return items_with, items_without


def make_show_dict(media_items: List) -> dict:
    """
    Convert a list of MediaItem objects into a show-season-episode dictionary
    Disregards any non-episode media items
    :param media_items: list of MediaItem objects
    :return: dict object with all episodes arranged by show-season-episode
    """
    show_dict = {}
    for item in media_items:
        if _object_has_attribute(object=item, attribute_name='type') and item.type == 'episode':
            if item.showTitle in show_dict.keys():
                if item.season in show_dict[item.showTitle].keys():
                    show_dict[item.showTitle][item.season][item.episode] = item
                else:
                    show_dict[item.showTitle][item.season] = {item.episode: item}
            else:
                show_dict[item.showTitle] = {item.season: {item.episode: item}}
    return show_dict


def order_show_dict(show_dict: dict) -> dict:
    """
    Sort a show dictionary in show-season-episode order
    :param show_dict: dictionary of shows in show-season-episode structure
    :return: dict object with all episodes arranged in order by show-season-episode
    """
    episode_ordered_dict = {}
    for show_name, seasons in show_dict.items():
        episode_ordered_dict[show_name] = {}
        for season_number, episodes in seasons.items():
            ordered_episodes = {episode_number: episode for episode_number, episode in
                                sorted(episodes.items(), key=lambda item: item[0])}
            episode_ordered_dict[show_name][season_number] = ordered_episodes
    season_ordered_dict = {}
    for show_name, seasons in episode_ordered_dict.items():
        ordered_seasons = {season_number: episodes for season_number, episodes in
                           sorted(seasons.items(), key=lambda item: item[0])}
        season_ordered_dict[show_name] = ordered_seasons
    return season_ordered_dict


# Public Helpers
def remove_time_from_date(date_string: Union[datetime, str]) -> str:
    """
    Remove time, i.e. 00:00:00, from a datetime.datetime or string
    :param date_string: datetime.datetime object or string to convert
    :return: str without time, i.e. 2020-08-29
    """
    if type(date_string) == str:
        date_string = string_to_datetime(date_string=date_string)
    return date_string.strftime("%Y-%m-%d")


def get_year_from_date(date_string: Union[datetime, str]) -> int:
    """
    Extract year from a datetime.datetime or string
    :param date_string: datetime.datetime object or string
    :return: int of year, i.e. 2020
    """
    if type(date_string) == str:
        date_string = string_to_datetime(date_string=date_string)
    return int(date_string.strftime("%Y"))


def string_to_datetime(date_string: str, template: str = "%Y-%m-%dT%H:%M:%S") -> datetime:
    """
    Convert a string to a datetime.datetime object
    :param date_string: datetime string to convert
    :param template: (Optional) datetime template to use when parsing string
    :return: datetime.datetime object
    """
    if date_string.endswith('Z'):
        date_string = date_string[:-5]
    return datetime.strptime(date_string, template)


def adjust_datetime_for_timezone(local_time: datetime) -> datetime:
    """
    Shift datetime.datetime in regards to UTC time
    :param local_time: local time datetime.datetime object
    :return: Shifted datetime.datetime object
    """
    difference = datetime.now() - datetime.utcnow()
    return local_time - difference


def hours_difference_in_timezone() -> int:
    """
    Get the hours difference between local and UTC time
    :return: int number of hours
    """
    return int((datetime.utcnow() - datetime.now()).total_seconds() / 60 / 60)


def get_nearest_30_minute_mark() -> str:
    """
    Get the most recently past hour or half-hour time
    :return: str of datetime
    """
    now = datetime.utcnow()
    if now.minute >= 30:
        now = now.replace(second=0, microsecond=0, minute=30)
    else:
        now = now.replace(second=0, microsecond=0, minute=0)
    return now.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def get_milliseconds_between_two_hours(start_hour: int, end_hour: int) -> int:
    """
    Get how many milliseconds between two 24-hour hours
    :param start_hour: starting hour (in 24-hour time)
    :param end_hour: ending hour (in 24-hour time)
    :return: int of milliseconds between the two hours
    """
    start_date = datetime(2020, 1, 1, start_hour, 0)
    if end_hour < start_hour:
        end_date = datetime(2020, 1, 2, end_hour, 0)
    else:
        end_date = datetime(2020, 1, 1, end_hour, 0)
    return int((end_date - start_date).total_seconds()) * 1000


def get_milliseconds_between_two_datetimes(start_datetime: datetime, end_datetime: datetime) -> int:
    """
    Get how many milliseconds between two datetime.datetime objects
    :param start_datetime: starting datetime.datetime object
    :param end_datetime: ending datetime.datetime object
    :return: int of milliseconds between the two datetime.datetime objects
    """
    return int((end_datetime - start_datetime).total_seconds()) * 1000


def get_needed_flex_time(item_time_milliseconds: int, allowed_minutes_time_frame: int) -> int:
    """
    Get how many milliseconds needed to stretch an item's runtime to a specific interval length
    :param item_time_milliseconds: how long the item is in milliseconds
    :param allowed_minutes_time_frame: how long an interval the item is supposed to be, in minutes
    :return: int of milliseconds needed to stretch item
    """
    minute_start = (30 if datetime.utcnow().minute >= 30 else 0)

    allowed_milliseconds_time_frame = (allowed_minutes_time_frame + (minute_start % allowed_minutes_time_frame)) * \
                                      60 * 1000
    remainder = allowed_milliseconds_time_frame - (item_time_milliseconds % allowed_milliseconds_time_frame)
    if remainder == allowed_milliseconds_time_frame:
        return 0
    return remainder


def get_plex_indirect_uri(plex_server: PServer, force_update: bool = False) -> Union[str, None]:
    """
    Get the indirect URI (ex. http://192.168.1.1-xxxxxxxxxxxxxxxx.plex.direct) for a Plex server
    :param plex_server: plexapi.server.PlexServer to get URI from
    :param force_update: ignore cached results, force an update
    :return: URI string or None
    """
    if _uris.get(plex_server.friendlyName) and not force_update:
        return _uris[plex_server.friendlyName]
    headers = {
        'Accept': 'application/json',
        'X-Plex-Product': 'dizqueTV-Python',
        'X-Plex-Version': 'Plex OAuth',
        'X-Plex-Client-Identifier': 'dizqueTV-Python',
        'X-Plex-Model': 'Plex OAuth',
        'X-Plex-Token': plex_server._token
    }
    response = requests.get(url="https://plex.tv/api/v2/resources?includeHttps=1", headers=headers)
    if response:
        json_data = response.json()
        for server in json_data:
            if server['name'] == plex_server.friendlyName:
                _uris[plex_server.friendlyName] = server['connections'][0]['uri']
                return server['connections'][0]['uri']
    return None


def get_plex_access_token(plex_server: PServer, force_update: bool = False) -> Union[str, None]:
    """
    Get the access token for a Plex server
    :param plex_server: plexapi.server.PlexServer to get access token from
    :param force_update: ignore cached results, force an update
    :return: Access token string or None
    """
    if not force_update:
        return plex_server._token
    headers = {
        'Accept': 'application/json',
        'X-Plex-Product': 'dizqueTV-Python',
        'X-Plex-Version': 'Plex OAuth',
        'X-Plex-Client-Identifier': 'dizqueTV-Python',
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


def dict_to_json(dictionary: dict) -> json:
    """
    Convert a dictionary to valid JSON
    :param dictionary: Dictionary to convert
    :return: JSON representation of dictionary
    """
    return json.dumps(dictionary)


def random_choice(items: List):
    """
    Get a random item from a list
    :param items: list of items
    :return: random item
    """
    return random.choice(items)


def shuffle(items: List) -> bool:
    """
    Randomize the order of the items in a list in-place
    :param items: list of items to shuffle
    :return: True if successful, False if unsuccessful
    """
    try:
        random.shuffle(items)
        return True
    except:
        pass
    return False


def rotate_items(items: List, shift_index: int = None) -> List:
    """
    Rotate items in a list by a specific number of steps
    :param items: list of items
    :param shift_index: Optional index to shift list by. Otherwise random
    :return: rotated list of items
    """
    if not shift_index:
        shift_index = random.randint(0, len(items) - 1)
    collection_list = collections.deque(items)
    collection_list.rotate(shift_index)
    return list(collection_list)


def remove_duplicates(items: List) -> List:
    """
    Remove duplicate items from a list
    "Duplicate" objects must be exactly the same (all attributes)
    :param items: list of items to parse
    :return: list of filtered items
    """
    return list(set(items))


def remove_duplicates_by_attribute(items: List, attribute_name: str) -> List:
    """
    Remove duplicate items from a list, comparing on a specific attribute
    :param items: list of items to parse
    :param attribute_name: name of attribute to check by
    :return: list of filtered items
    """
    filtered = []
    filtered_attr = []
    for item in items:
        attr = getattr(item, attribute_name)
        if attr not in filtered_attr:
            filtered.append(item)
            filtered_attr.append(attr)
    return filtered
