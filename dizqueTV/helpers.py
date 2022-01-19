import collections
import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Union, Tuple

import numpy.random as numpy_random
from plexapi.audio import Track
from plexapi.server import PlexServer as PServer
from plexapi.video import Video, Movie, Episode

import dizqueTV.dizquetv_requests as requests
from dizqueTV.exceptions import MissingSettingsError
from dizqueTV.models.media import Program, Redirect, FillerItem

_access_tokens = {}
_uris = {}


# Internal Helpers
def _combine_settings_add_new(new_settings_dict: dict,
                              default_dict: dict,
                              ignore_keys: List = None) -> dict:
    """
    Build a complete dictionary for new settings, using old settings as a base
    Add new keys to template.

    :param new_settings_dict: Dictionary of new settings kwargs
    :type new_settings_dict: dict
    :param default_dict: Current settings
    :type default_dict: dict
    :param ignore_keys: List of keys to ignore when combining dictionaries
    :type ignore_keys: list, optional
    :return: Dictionary of new settings
    :rtype: dict
    """
    if not ignore_keys:
        ignore_keys = []
    for k, v in new_settings_dict.items():
        if k in ignore_keys:
            pass
        else:
            default_dict[k] = v
    return default_dict


def _combine_settings(new_settings_dict: dict,
                      default_dict: dict,
                      ignore_keys: List = None) -> dict:
    """
    Build a complete dictionary for new settings, using old settings as a base
    Do not add new keys to template.

    :param new_settings_dict: Dictionary of new settings kwargs
    :type new_settings_dict: dict
    :param default_dict: settings template
    :type default_dict: dict
    :param ignore_keys: List of keys to ignore when combining dictionaries
    :type ignore_keys: list, optional
    :return: Dictionary of new settings
    :rtype: dict
    """
    if not ignore_keys:
        ignore_keys = []
    for k, v in new_settings_dict.items():
        if k in ignore_keys:
            pass
        else:
            # only add the key if it's in the template
            if k in default_dict.keys():
                default_dict[k] = v
    return default_dict


def _combine_settings_enforce_types(new_settings_dict: dict,
                                    default_dict: dict,
                                    template_dict: dict,
                                    ignore_keys: List = None) -> dict:
    """
    Build a complete dictionary for new settings, using old settings as a base
    Do not add new keys to template
    Enforce default options

    :param new_settings_dict: Dictionary of new settings kwargs
    :type new_settings_dict: dict
    :param template_dict: settings template
    :type template_dict: dict
    :param default_dict: default settings
    :type default_dict: dict
    :param ignore_keys: List of keys to ignore when combining dictionaries
    :type ignore_keys: list, optional
    :return: Dictionary of new settings
    :rtype: dict
    """
    if not ignore_keys:
        ignore_keys = []
    for k in default_dict.keys():
        if k in ignore_keys:
            # don't bother checking this key, just leave it with the default
            pass
        else:
            # only accept the override value if it's of the correct type
            if (type(new_settings_dict[k]) == template_dict[k]) or (new_settings_dict[k] in template_dict[k]):
                default_dict[k] = new_settings_dict[k]
    return default_dict


def _filter_dictionary(new_dictionary: dict, template_dict: dict) -> dict:
    """
    Remove key-value pairs from new_dictionary that are not present in template_dict

    :param new_dictionary: Dictionary of key-value pairs
    :type new_dictionary: dict
    :param template_dict: Dictionary of accepted key-value pairs
    :type template_dict: dict
    :return: Dictionary with only accepted key-value pairs
    :rtype: dict
    """
    final_dict = {}
    for k, v in new_dictionary.items():
        if k in template_dict.keys():
            final_dict[k] = v
    return final_dict


def _settings_are_complete(new_settings_dict: dict, template_settings_dict: json, ignore_keys: List = None) -> bool:
    """
    Check that all elements from the settings template are present in the new settings

    :param new_settings_dict: Dictionary of new settings kwargs
    :type new_settings_dict: dict
    :param template_settings_dict: Template of settings
    :type template_settings_dict: dict
    :param ignore_keys: List of keys to ignore when analyzing completeness
    :type ignore_keys: list, optional
    :return: True if valid, raise dizqueTV.exceptions.IncompleteSettingsError if not valid
    :rtype: bool
    """
    if not ignore_keys:
        ignore_keys = []
    for k in template_settings_dict.keys():
        if k not in new_settings_dict.keys():
            # or not isinstance(new_settings_dict[k], type(template_settings_dict[k]))
            if k in ignore_keys:
                pass
            else:
                raise MissingSettingsError(f"Missing setting: {k}")
    return True


def convert_icon_position(position_text: str) -> str:
    """
    Convert ex. Top Left -> 0

    :param position_text: position
    :type position_text: str
    :return: String of an int
    :rtype: str
    """
    if type(position_text) == int:
        return str(position_text)
    position_text = position_text.lower()
    if 'top' in position_text:
        if 'left' in position_text:
            return '0'
        if 'right' in position_text:
            return '1'
    if 'bottom' in position_text:
        if 'left' in position_text:
            return '2'
    return '3'


def file_exists(file_path: str) -> bool:
    """
    Check if provided file_path exists

    :param file_path: path to a file
    :type file_path: str
    :return: Whether file exists or not
    :rtype: bool
    """
    return os.path.exists(file_path)


def read_file_bytes(file_path: str):
    """
    Read a file as bytes

    :param file_path: path to file
    :type file_path: str
    :return:
    :rtype:
    """
    return open(file_path, 'rb')


def _object_has_attribute(obj: object, attribute_name: str) -> bool:
    """
    Check if an object has an attribute (exists and is not None)

    :param obj: object to check
    :type obj: object
    :param attribute_name: name of attribute to find
    :type attribute_name: str
    :return: True if exists and is not None, False otherwise
    :rtype: bool
    """
    if hasattr(obj, attribute_name):
        if getattr(obj, attribute_name) is not None:
            return True
    return False


def _make_program_dict_from_plex_item(plex_item: Union[Video, Movie, Episode, Track], plex_server: PServer) -> dict:
    """
    Build a dictionary for a Program using a PlexAPI Video, Movie, Episode or Track object

    :param plex_item: plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode or plexapi.audio.Track object
    :type plex_item: Union[plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode, plexapi.audio.Track]
    :param plex_server: plexapi.server.PlexServer object
    :type plex_server: plexapi.server.PlexServer
    :return: dict of Plex item information
    :rtype: dict
    """
    item_type = plex_item.type
    plex_media_item_part = plex_item.media[0].parts[0]
    plex_uri = get_plex_indirect_uri(plex_server=plex_server)
    plex_token = get_plex_access_token(plex_server=plex_server)
    data = {
        'title': plex_item.title,
        'key': plex_item.key,
        'ratingKey': str(plex_item.ratingKey),
        'icon': f"{plex_uri}{plex_item.thumb}?X-Plex-Token={plex_token}",
        'type': item_type,
        'duration': (plex_item.duration if (hasattr(plex_item, 'duration') and plex_item.duration) else 0),
        'summary': plex_item.summary,
        'rating': "" if plex_item.type == 'track' else plex_item.contentRating,
        'date': (remove_time_from_date(plex_item.originallyAvailableAt)
                 if (hasattr(plex_item, 'originallyAvailableAt') and plex_item.originallyAvailableAt)
                 else '1900-01-01'),
        'year': (get_year_from_date(plex_item.originallyAvailableAt)
                 if (hasattr(plex_item, 'originallyAvailableAt') and plex_item.originallyAvailableAt)
                 else '1900'),
        'plexFile': plex_media_item_part.key,
        'file': plex_media_item_part.file,
        'showTitle': (plex_item.title if item_type == 'movie' else plex_item.grandparentTitle),
        'episode': (1 if item_type == 'movie' else int(plex_item.index)),
        'season': (1 if item_type == 'movie' else int(plex_item.parentIndex)),
        'serverKey': plex_server.friendlyName
    }
    if plex_item.type == 'episode':
        data['episodeIcon'] = f"{plex_uri}{plex_item.thumb}?X-Plex-Token={plex_token}"
        data['seasonIcon'] = f"{plex_uri}{plex_item.parentThumb if plex_item.parentThumb else plex_item.grandparentThumb}?X-Plex-Token={plex_token}"
        data['showIcon'] = f"{plex_uri}{plex_item.grandparentThumb}?X-Plex-Token={plex_token}"
        data['icon'] = data['showIcon']
    return data


def _make_filler_dict_from_plex_item(plex_item: Union[Video, Movie, Episode, Track], plex_server: PServer) -> dict:
    """
    Build a dictionary for a FillerItem using a PlexAPI Video, Movie, Episode or Track object

    :param plex_item: plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode or plexapi.audio.Track object
    :type plex_item: Union[plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode, plexapi.audio.Track]
    :param plex_server: plexapi.server.PlexServer object
    :type plex_server: plexapi.server.PlexServer
    :return: dict of Plex item information
    :rtype: dict
    """
    item_type = plex_item.type
    plex_media_item_part = plex_item.media[0].parts[0]
    data = {
        'title': plex_item.title,
        'key': plex_item.key,
        'ratingKey': str(plex_item.ratingKey),
        'icon': plex_item.thumb,
        'type': item_type,
        'duration': (plex_item.duration if (hasattr(plex_item, 'duration') and plex_item.duration) else 0),
        'summary': plex_item.summary,
        'date': (remove_time_from_date(plex_item.originallyAvailableAt)
                 if (hasattr(plex_item, 'originallyAvailableAt') and plex_item.originallyAvailableAt)
                 else '1900-01-01'),
        'year': (get_year_from_date(plex_item.originallyAvailableAt)
                 if (hasattr(plex_item, 'originallyAvailableAt') and plex_item.originallyAvailableAt)
                 else '1900-01-01'),
        'plexFile': plex_media_item_part.key,
        'file': plex_media_item_part.file,
        'showTitle': (plex_item.title if item_type == 'movie' else plex_item.grandparentTitle),
        'episode': (1 if item_type == 'movie' else int(plex_item.index)),
        'season': (1 if item_type == 'movie' else int(plex_item.parentIndex)),
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
    :type plex_server: plexapi.server.PlexServer
    :param auto_reload_guide: Auto-update guide
    :type auto_reload_guide: bool, optional
    :param auto_reload_channels: Auto-update channels
    :type auto_reload_channels: bool, optional
    :return: dict of PlexServer item information
    :rtype: dict
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
    :type items: list
    :param attribute_name: Name of attribute to look for
    :type attribute_name: str
    :return: list_with, list_without
    :rtype: [list, list]
    """
    items_with = []
    items_without = []
    for item in items:
        if _object_has_attribute(obj=item, attribute_name=attribute_name):
            items_with.append(item)
        else:
            items_without.append(item)
    return items_with, items_without


def get_items_of_type(item_type: str, items: List) -> List:
    """
    Get all items with 'type' = X

    :param item_type: 'type' to look for
    :type item_type: str
    :param items: list of items to filter
    :type items: list
    :return: list of items with 'type' = X
    :rtype: list
    """
    return [item for item in items if
            (_object_has_attribute(obj=item, attribute_name='type') and item.type == item_type)]


def get_items_of_not_type(item_type: str, items: List) -> List:
    """
    Get all items without 'type' = X

    :param item_type: 'type' to look for
    :type item_type: str
    :param items: list of items to filter
    :type items: list
    :return: list of items without 'type' = X
    :rtype: list
    """
    return [item for item in items if
            (_object_has_attribute(obj=item, attribute_name='type') and item.type != item_type)]


def get_non_shows(media_items: List) -> List:
    """
    Get all non_show items

    :param media_items: list of MediaItem objects
    :type media_items: List[MediaItem]
    :return: list of non-show MediaItem objects
    :rtype: list
    """
    return [item for item in media_items if
            ((_object_has_attribute(obj=item, attribute_name='type') and item.type != 'episode') or
             (_object_has_attribute(obj=item, attribute_name='season') and not item.season))]


def make_show_dict(media_items: List) -> dict:
    """
    Convert a list of MediaItem objects into a show-season-episode dictionary
    Disregards any non-episode media items

    :param media_items: list of MediaItem objects
    :type media_items: List[MediaItem]
    :return: dict object with all episodes arranged by show-season-episode
    :rtype: dict
    """
    show_dict = {}
    for item in media_items:
        if _object_has_attribute(obj=item, attribute_name='type') and item.type == 'episode' and item.episode:
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
    :type show_dict: dict
    :return: dict object with all episodes arranged in order by show-season-episode
    :rtype: dict
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


def add_durations_to_show_dict(show_dict: dict) -> dict:
    """
    Add episode, season and show duration to show_dict

    :param show_dict: dictionary of shows in show-season-episode structure
    :type show_dict: dict
    :return: dict object with duration included for each episode, season and show
    :rtype: dict
    """
    sorted_shows = {}
    for show_name, seasons in show_dict.items():
        sorted_shows[show_name] = {'seasons': {}, 'duration': 0}
        for season_number, episodes in seasons.items():
            sorted_shows[show_name]['seasons'][season_number] = {'episodes': {}, 'duration': 0}
            for episode_number, episode in episodes.items():
                episode_dict = {'episode': episode, 'duration': episode.duration}
                sorted_shows[show_name]['seasons'][season_number]['episodes'][episode_number] = episode_dict
                sorted_shows[show_name]['seasons'][season_number]['duration'] += episode.duration
                sorted_shows[show_name]['duration'] += episode.duration
    return sorted_shows


def condense_show_dict(show_dict: dict) -> dict:
    """
    Condense a show-season-episode dictionary into a show-episode dictionary
    Disregards any non-episode media items
    DO NOT PASS IN A SHOW_DICT WITH DURATIONS

    :param show_dict: dictionary of shows in show-season-episode structure
    :type show_dict: dict
    :return: dict object with all episodes arranged by show-episode
    :rtype: dict
    """
    sorted_shows = {'count': 0, 'shows': {}}
    for show_name, seasons in show_dict.items():
        sorted_shows['shows'][show_name] = {'episodes': [], 'count': 0}
        for season_number, episodes in seasons.items():
            for episode_number, episode in episodes.items():
                sorted_shows['shows'][show_name]['episodes'].append(episode)
                sorted_shows['shows'][show_name]['count'] += 1
                sorted_shows['count'] += 1
    return sorted_shows


# Public Helpers
def remove_time_from_date(date_string: Union[datetime, str]) -> str:
    """
    Remove time, i.e. 00:00:00, from a datetime.datetime or string

    :param date_string: datetime.datetime object or string to convert
    :type date_string: Union[datetime.datetime, str]
    :return: str without time, i.e. 2020-08-29
    :rtype: str
    """
    if type(date_string) == str:
        date_string = string_to_datetime(date_string=date_string)
    return date_string.strftime("%Y-%m-%d")


def get_year_from_date(date_string: Union[datetime, str]) -> int:
    """
    Extract year from a datetime.datetime or string

    :param date_string: datetime.datetime object or string
    :type date_string: Union[datetime.datetime, str]
    :return: int of year, i.e. 2020
    :rtype: int
    """
    if type(date_string) == str:
        date_string = string_to_datetime(date_string=date_string)
    return int(date_string.strftime("%Y"))


def string_to_datetime(date_string: str, template: str = "%Y-%m-%dT%H:%M:%S") -> datetime:
    """
    Convert a datetime string to a datetime.datetime object

    :param date_string: datetime string to convert
    :type date_string: str
    :param template: (Optional) datetime template to use when parsing string
    :type template: str, optional
    :return: datetime.datetime object
    :rtype: datetime.datetime
    """
    if date_string.endswith('Z'):
        date_string = date_string[:-5]
    return datetime.strptime(date_string, template)


def datetime_to_string(datetime_object: datetime, template: str = "%Y-%m-%dT%H:%M:%S.000Z") -> str:
    """
    Convert a datetime.datetime object to a string

    :param datetime_object: datetime.datetime object to convert
    :type datetime_object: datetime.datetime
    :param template: (Optional) datetime template to use when parsing string
    :type template: str, optional
    :return: str representation of datetime
    :rtype: str
    """
    return datetime_object.strftime(template)


def string_to_time(time_string: str, template: str = "%H:%M:%S") -> datetime:
    """
    Convert a time string to a datetime.datetime object

    :param time_string: datetime string to convert
    :type time_string: str
    :param template: (Optional) datetime template to use when parsing string
    :type template: str, optional
    :return: datetime.datetime object
    :rtype: datetime.datetime
    """
    if time_string.endswith('Z'):
        time_string = time_string[:-5]
    return datetime.strptime(time_string, template)


def time_to_string(datetime_object: datetime, template: str = "%H:%M:%S") -> str:
    """
    Convert a datetime.datetime object to a string

    :param datetime_object: datetime.datetime object to convert
    :type datetime_object: datetime.datetime
    :param template: (Optional) datetime template to use when parsing string
    :type template: str, optional
    :return: str representation of datetime
    :rtype: str
    """
    return datetime_object.strftime(template)


def duration_to_string(milliseconds: int) -> str:
    """
    Convert a millisecond duration to a duration string

    :param milliseconds: duration in milliseconds
    :type milliseconds: int
    :return: duration string "%H
    :rtype: str
    """
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%02d:%02d:%02d.%01d" % (hours, minutes, seconds, milliseconds)


def adjust_datetime_for_timezone(local_time: datetime) -> datetime:
    """
    Shift datetime.datetime in regards to UTC time

    :param local_time: local time datetime.datetime object
    :type local_time: datetime.datetime
    :return: Shifted datetime.datetime object
    :rtype: datetime.datetime
    """
    difference = datetime.now() - datetime.utcnow()
    return local_time - difference


def hours_difference_in_timezone() -> int:
    """
    Get the hours difference between local and UTC time

    :return: int number of hours
    :rtype: int
    """
    return int((datetime.utcnow() - datetime.now()).total_seconds() / 60 / 60)


def shift_time(starting_time: datetime,
               seconds: int = 0,
               minutes: int = 0,
               hours: int = 0,
               days: int = 0,
               months: int = 0,
               years: int = 0) -> datetime:
    """
    Shift a time forward or backwards

    :param starting_time: datetime.datetime object
    :type starting_time: datetime.datetime
    :param seconds: how many seconds
    :type seconds: int, optional
    :param minutes: how many minutes
    :type minutes: int, optional
    :param hours: how many hours
    :type hours: int, optional
    :param days: how many days
    :type days: int, optional
    :param months: how many months (assume 30 days in month)
    :type months: int, optional
    :param years: how many years (assume 365 days in year)
    :type years: int, optional
    :return: shifted datetime.datetime object
    :rtype: datetime.datetime
    """
    days = days + (30 * months) + (365 * years)
    return starting_time + timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)


def get_nearest_30_minute_mark() -> str:
    """
    Get the most recently past hour or half-hour time

    :return: str of datetime
    :rtype: str
    """
    now = datetime.utcnow()
    if now.minute >= 30:
        now = now.replace(second=0, microsecond=0, minute=30)
    else:
        now = now.replace(second=0, microsecond=0, minute=0)
    return now.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def convert_24_time_to_milliseconds_past_midnight(time_string: str) -> int:
    """
    Get milliseconds between time_string and midnight

    :param time_string: readable 24-hour time (ex. 00:00:00, 05:30:15, 20:08:30)
    :type time_string: str
    :return: int of milliseconds since midnight
    :rtype: int
    """
    hour_minute_second = time_string.split(':')
    if len(hour_minute_second) < 2 or len(hour_minute_second) > 4:
        raise Exception("Time string must be in two-digit format hour:minute:second")
    if len(hour_minute_second) == 2:
        time_string += ":00"
    time_in_datetime = string_to_time(time_string=time_string)
    midnight = string_to_time(time_string="00:00:00")
    return get_milliseconds_between_two_datetimes(start_datetime=midnight, end_datetime=time_in_datetime)


def get_milliseconds_between_two_hours(start_hour: int, end_hour: int) -> int:
    """
    Get how many milliseconds between two 24-hour hours

    :param start_hour: starting hour (in 24-hour time)
    :type start_hour: int
    :param end_hour: ending hour (in 24-hour time)
    :type end_hour: int
    :return: int of milliseconds between the two hours
    :rtype: int
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
    :type start_datetime: datetime.datetime
    :param end_datetime: ending datetime.datetime object
    :type end_datetime: datetime.datetime
    :return: int of milliseconds between the two datetime.datetime objects
    :rtype: int
    """
    return int((end_datetime - start_datetime).total_seconds()) * 1000


def get_needed_flex_time(item_time_milliseconds: int, allowed_minutes_time_frame: int) -> int:
    """
    Get how many milliseconds needed to stretch an item's runtime to a specific interval length

    :param item_time_milliseconds: how long the item is in milliseconds
    :type item_time_milliseconds: int
    :param allowed_minutes_time_frame: how long an interval the item is supposed to be, in minutes
    :type allowed_minutes_time_frame: int
    :return: int of milliseconds needed to stretch item
    :rtype: int
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
    :type plex_server: plexapi.server.PlexServer
    :param force_update: ignore cached results, force an update
    :type force_update: bool, optional
    :return: URI string or None
    :rtype: str | None
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
    :type plex_server: plexapi.server.PlexServer
    :param force_update: ignore cached results, force an update
    :type force_update: bool, optional
    :return: Access token string or None
    :rtype: str | None
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
    :type dictionary: dict
    :return: JSON representation of dictionary
    :rtype: str
    """
    return json.dumps(dictionary)


# Sorting
def random_choice(items: List):
    """
    Get a random item from a list

    :param items: list of items
    :type items: list
    :return: random item
    :rtype: object
    """
    return random.choice(items)


def weighted_choice_by_probabilities(items: List, probabilities: List[float]):
    """
    Get a random item from a weighted list

    :param items: list of items
    :type items: list
    :param probabilities: list of corresponding item percentage (must total 1)
    :type probabilities: list of floats
    :return: random item
    :rtype: object
    """
    choice_list = numpy_random.choice(a=items, size=1, p=probabilities)
    return choice_list[0]


def weighted_choice_by_sizes_lists(items: List, sizes: List[int]):
    """
    Get a random item from a weighted list

    :param items: list of items
    :type items: list
    :param sizes: list of corresponding item sizes
    :type sizes: list of ints
    :return: random item
    :rtype: object
    """
    total_items = sum(sizes)
    percentages = []
    for size in sizes:
        percentages.append(size / total_items)
    return weighted_choice_by_probabilities(items=items, probabilities=percentages)


def weighted_choice_by_sizes_dict(items_and_sizes: dict):
    """
    Get a random item from a weighted dict

    :param items_and_sizes: dict of items and sizes
    :type items_and_sizes: dict
    :return: random item
    :rtype: object
    """
    total_items = sum(items_and_sizes.values())
    percentages = []
    for size in items_and_sizes.values():
        percentages.append(size / total_items)
    items = []
    for item in items_and_sizes.keys():
        items.append(item)
    return weighted_choice_by_probabilities(items=items, probabilities=percentages)


def shuffle(items: List) -> bool:
    """
    Randomize the order of the items in a list in-place

    :param items: list of items to shuffle
    :type items: list
    :return: True if successful, False if unsuccessful
    :rtype: bool
    """
    try:
        random.shuffle(items)
        return True
    except:
        return False


def rotate_items(items: List, shift_index: int = None) -> List:
    """
    Rotate items in a list by a specific number of steps

    :param items: list of items
    :type items: list
    :param shift_index: Optional index to shift list by. Otherwise random
    :type shift_index: int, optional
    :return: rotated list of items
    :rtype: list[object]
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
    :type items: list
    :return: list of filtered items
    :rtpye: list[object]
    """
    return list(set(items))


def remove_duplicates_by_attribute(items: List, attribute_name: str) -> List:
    """
    Remove duplicate items from a list, comparing on a specific attribute

    :param items: list of items to parse
    :type items: list
    :param attribute_name: name of attribute to check by
    :type attribute_name: str
    :return: list of filtered items
    :rtype: list[object]
    """
    filtered = []
    filtered_attr = []
    for item in items:
        attr = getattr(item, attribute_name)
        if not attr:
            filtered.append(item)
        elif attr not in filtered_attr:
            filtered.append(item)
            filtered_attr.append(attr)
    return filtered


def sort_media_alphabetically(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Sort media items alphabetically.
    Note: Shows will be grouped and sorted by series title, but episodes may be out of order.
    Items without titles will be appended at the end of the list

    :param media_items: List of Program and FillerItem objects
    :type media_items: List[Union[Program, FillerItem]]
    :return: List of Program and FillerItem objects
    :rtype: List[Union[Program, FillerItem]]
    """
    items_with_titles, items_without_titles = _separate_with_and_without(items=media_items,
                                                                         attribute_name='title')
    sorted_items = sorted(items_with_titles, key=lambda x: (x.showTitle if x.type == 'episode' else x.title))
    sorted_items.extend(items_without_titles)
    return sorted_items


def sort_media_by_release_date(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Sort media items by release date.
    Note: Items without release dates are appended (alphabetically) at the end of the list

    :param media_items: List of Program and FillerItem objects
    :type media_items: List[Union[Program, FillerItem]]
    :return: List of Program and FillerItem objects
    :rtype: List[Union[Program, FillerItem]]
    """
    items_with_dates, items_without_dates = _separate_with_and_without(items=media_items,
                                                                       attribute_name='date')
    sorted_items = sorted(items_with_dates, key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"))
    sorted_items.extend(sort_media_alphabetically(media_items=items_without_dates))
    return sorted_items


def _sort_shows_by_season_order(shows_dict: dict) -> List[Union[Program, FillerItem]]:
    """
    Sort a show dictionary by series-season-episode.
    Series are ordered alphabetically

    :param shows_dict: Series-season-episode dictionary
    :type shows_dict: dict
    :return: List of Program and FillerItem objects
    :rtype: List[Union[Program, FillerList]]
    """
    sorted_list = []
    sorted_shows = sorted(shows_dict.items(), key=lambda show_name: show_name)
    for show in sorted_shows:
        sorted_seasons = sorted(show[1].items(), key=lambda season_number: season_number)
        for season in sorted_seasons:
            sorted_episodes = sorted(season[1].items(), key=lambda episode_number: episode_number)
            for item in sorted_episodes:
                sorted_list.append(item[1])
    return sorted_list


def sort_media_by_season_order(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Sort media items by season order.
    Note: Series are ordered alphabetically, movies appended (alphabetically) at the end of the list.

    :param media_items: List of Program and FillerItem objects
    :type media_items: List[Union[Program, FillerItem]]
    :return: List of Program and FillerItem objects
    :rtype: List[Union[Program, FillerList]]
    """
    non_shows = get_non_shows(media_items=media_items)
    show_dict = make_show_dict(media_items=media_items)
    sorted_shows = _sort_shows_by_season_order(shows_dict=show_dict)
    sorted_movies = sort_media_alphabetically(media_items=non_shows)
    sorted_all = sorted_shows + sorted_movies
    return sorted_all


def sort_media_by_duration(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Sort media by duration.
    Note: Automatically removes redirect items

    :param media_items: List of Program and FillerItem objects
    :type media_items: List[Union[Program, FillerList]]
    :return: List of Program and FillerItem objects
    :rtype: List[Union[Program, FillerList]]
    """
    non_redirects = [item for item in media_items if
                     (_object_has_attribute(obj=item, attribute_name='duration')
                      and _object_has_attribute(obj=item, attribute_name='type')
                      and item.type != 'redirect')]
    sorted_media = sorted(non_redirects, key=lambda x: x.duration)
    return sorted_media


def sort_media_randomly(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Sort media randomly.

    :param media_items: List of Program and FillerItem objects
    :type media_items: List[Union[Program, FillerList]]
    :return: List of Program and FillerItem objects
    :rtype: List[Union[Program, FillerList]]
    """
    shuffle(items=media_items)
    return media_items


def sort_media_cyclical_shuffle(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Sort media cyclically.
    Note: Automatically removes FillerItem objects

    :param media_items: List of Program and FillerItem objects
    :type media_items: List[Union[Program, FillerList]]
    :return: List of Program objects, FillerItem objects removed
    :rtype: List[Union[Program, FillerList]]
    """
    total_item_count = len(media_items)
    non_shows = get_non_shows(media_items=media_items)
    shuffle(items=non_shows)
    show_dict = make_show_dict(media_items=media_items)
    show_dict = order_show_dict(show_dict=show_dict)
    total_episode_count = 0
    show_list = {}
    index = 0
    index_list = []
    for show_name, seasons in show_dict.items():
        season_episode_order = []
        for season_number, episodes in seasons.items():
            for _, episode in episodes.items():
                season_episode_order.append(episode)
                total_episode_count += 1
        show_cyclical_order = rotate_items(items=season_episode_order)
        show_list[index] = show_cyclical_order
        index_list.append(index)
        index += 1
    show_list['remaining_episode_count'] = total_episode_count
    final_list = []
    while len(final_list) != total_item_count:
        categories_and_sizes = {
            'show': show_list['remaining_episode_count'],
            'non_show': len(non_shows)
        }
        if 'non_show' in categories_and_sizes.keys() and len(non_shows) == 0:
            del categories_and_sizes['non_show']
        if 'show' in categories_and_sizes.keys() and show_list['remaining_episode_count'] == 0:
            del categories_and_sizes['show']
        if not categories_and_sizes:
            break
        show_or_non_show = weighted_choice_by_sizes_dict(items_and_sizes=categories_and_sizes)
        if show_or_non_show == 'show':
            random_index = random_choice(items=index_list)  # failure 1
            new_item = show_list[random_index].pop(0)
            show_list['remaining_episode_count'] -= 1
            final_list.append(new_item)
            if len(show_list[random_index]) == 0:
                index_list.remove(random_index)
        else:
            new_item = non_shows.pop(0)
            final_list.append(new_item)
    return final_list


def sort_media_block_shuffle(media_items: List[Union[Program, FillerItem]],
                             block_length: int = 1,
                             randomize: bool = False) -> List[Union[Program, FillerItem]]:
    """
    Sort media with block shuffle.
    Default: Items are alternated one at a time, alphabetically
    Note: Automatically removes FillerItem objects

    :param media_items: List of Program and FillerItem objects
    :type media_items: List[Union[Program, FillerList]]
    :param block_length: length of each block of programming
    :type block_length: int, optional
    :param randomize: random length (up to block_length) and random order
    :type randomize: bool, optional
    :return: List of Program objects, FillerItem objects removed
    :rtype: List[Union[Program, FillerList]]
    """
    non_shows = get_non_shows(media_items=media_items)
    show_dict = make_show_dict(media_items=media_items)
    ordered_show_dict = order_show_dict(show_dict=show_dict)
    condensed_show_dict = condense_show_dict(show_dict=ordered_show_dict)
    final_show_list = []
    target_length = condensed_show_dict['count']
    if randomize:
        while len(final_show_list) < target_length:
            random_show_name = random.choice(list(condensed_show_dict['shows'].keys()))
            for _ in range(0, random.randint(1, block_length)):
                if len(condensed_show_dict['shows'][random_show_name]['episodes']) > 0:
                    final_show_list.append(condensed_show_dict['shows'][random_show_name]['episodes'].pop(0))
                else:
                    del condensed_show_dict['shows'][random_show_name]
                    break
    else:
        while len(final_show_list) < target_length:
            for show_name, data in condensed_show_dict['shows'].items():
                for _ in range(0, block_length):
                    if len(data['episodes']) > 0:
                        final_show_list.append(data['episodes'].pop(0))
                    else:
                        break
    final_list = final_show_list + non_shows
    return final_list


def balance_shows(media_items: List[Union[Program, FillerItem]], margin_of_correction: float = 0.1) -> \
        List[Union[Program, FillerItem]]:
    """
    Balance weights of the shows. Movies are untouched.

    :param media_items: List of Program and FillerItem objects
    :type media_items: List[Union[Program, FillerList]]
    :param margin_of_correction: Percentage over shortest time to use when assessing whether to add a new episode
    :type margin_of_correction: float, optional
    :return: List of Program and FillerItem objects
    :rtype: List[Union[Program, FillerList]]
    """
    non_shows = get_non_shows(media_items=media_items)
    show_dict = make_show_dict(media_items=media_items)
    ordered_show_dict = order_show_dict(show_dict=show_dict)
    ordered_show_dict_with_durations = add_durations_to_show_dict(show_dict=ordered_show_dict)
    show_durations = []
    for show_name in ordered_show_dict_with_durations.keys():
        show_durations.append(ordered_show_dict_with_durations[show_name]['duration'])
    shortest_show_length = min(show_durations)
    margin = 1 + margin_of_correction
    final_shows = []
    for show_name, show_data in ordered_show_dict_with_durations.items():
        show_running_duration = 0
        continue_with_show = True
        for season_number, season_data in show_data['seasons'].items():
            if not continue_with_show:
                break
            for episode_number, episode_data in season_data['episodes'].items():
                if not continue_with_show:
                    break
                potential_show_duration = show_running_duration + episode_data['duration']
                if (float(potential_show_duration) / float(shortest_show_length)) <= margin:
                    final_shows.append(episode_data['episode'])
                    show_running_duration += episode_data['duration']
                else:
                    continue_with_show = False
    sorted_movies = sort_media_alphabetically(media_items=non_shows)
    sorted_all = final_shows + sorted_movies
    return sorted_all


def remove_non_programs(media_items: List[Union[Program, Redirect, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Remove all non-programs from list of media items.

    :param media_items: List of Program, Redirect and FillerItem objects
    :type media_items: List[Union[Program, FillerList]]
    :return: List of Program and FillerItem objects
    :rtype: List[Union[Program, FillerList]]
    """
    return [item for item in media_items if
            (_object_has_attribute(obj=item, attribute_name='type')
             and item.type != 'redirect')]


def remove_duplicate_media_items(media_items: List[Union[Program, Redirect, FillerItem]]) -> \
        List[Union[Program, FillerItem]]:
    """
    Remove duplicate items from list of media items.
    Check by ratingKey.
    Note: Automatically removes redirect items

    :param media_items: List of Program and FillerItem objects
    :type media_items: List[Union[Program, FillerList]]
    :return: List of Program and FillerItem objects
    :rtype: List[Union[Program, FillerList]]
    """
    non_redirects = remove_non_programs(media_items=media_items)
    return remove_duplicates_by_attribute(items=non_redirects, attribute_name='ratingKey')


def _get_first_x_minutes_of_programs(programs: List[Union[Program, Redirect, FillerItem]],
                                     minutes: int) -> Tuple[List[Union[Program, Redirect, FillerItem]], int]:
    """
    Keep building a list of programs in order until a duration limit is met.

    :param programs: list of Program objects to pull from
    :type programs: List[Union[Program, Redirect, FillerList]]
    :param minutes: threshold, in minutes
    :type minutes: int
    :return: list of Program objects, total running time in milliseconds
    :rtype: Tuple[List[Union[Program, Redirect, FillerList]], int]
    """
    milliseconds = minutes * 60 * 1000
    running_total = 0
    programs_to_return = []
    for program in programs:
        if (running_total + program.duration) <= milliseconds:
            running_total += program.duration
            programs_to_return.append(program)
        else:
            break
    return programs_to_return, running_total


def _get_first_x_minutes_of_programs_return_unused(programs: List[Union[Program, Redirect, FillerItem]],
                                                   minutes: int) -> Tuple[List[Union[Program, Redirect, FillerItem]],
                                                                          int,
                                                                          List[Union[Program, Redirect, FillerItem]]]:
    """
    Keep building a list of programs in order until a duration limit is met.

    :param programs: list of Program objects to pull from
    :type programs: List[Union[Program, Redirect, FillerList]]
    :param minutes: threshold, in minutes
    :type minutes: int
    :return: list of Program objects, total running time in milliseconds, unused Programs
    :rtype: Tuple[List[Union[Program, Redirect, FillerList]], int, List[Union[Program, Redirect, FillerList]]]
    """
    milliseconds = minutes * 60 * 1000
    running_total = 0
    leftover_programs = []
    programs_to_return = []
    for program in programs:
        if (running_total + program.duration) <= milliseconds:
            running_total += program.duration
            programs_to_return.append(program)
        else:
            break
    for program in programs:
        if program not in programs_to_return:
            leftover_programs.append(program)
    return programs_to_return, running_total, leftover_programs
