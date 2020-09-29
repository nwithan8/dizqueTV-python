import json
from datetime import datetime, timedelta
from typing import List, Union, Tuple
import collections
import random

from plexapi.video import Video, Movie, Episode
from plexapi.server import PlexServer as PServer

from dizqueTV.exceptions import MissingSettingsError, NotRemoteObjectError
import dizqueTV.requests as requests
from dizqueTV.media import Program, Redirect, FillerItem

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
            if k in ['_id', 'id'] and ignore_id:
                pass
            else:
                raise MissingSettingsError(f"Missing setting: {k}")
    return True


def convert_icon_position(position_text) -> str:
    """
    Convert ex. Top Left -> 0
    :param position_text: position
    :return: str(int)
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
        'duration': (plex_item.duration if (hasattr(plex_item, 'duration') and plex_item.duration) else 0),
        'summary': plex_item.summary,
        'rating': plex_item.contentRating,
        'date': (remove_time_from_date(plex_item.originallyAvailableAt)
                 if (hasattr(plex_item, 'originallyAvailableAt') and plex_item.originallyAvailableAt)
                 else '1900-01-01'),
        'year': (get_year_from_date(plex_item.originallyAvailableAt)
                 if (hasattr(plex_item, 'originallyAvailableAt') and plex_item.originallyAvailableAt)
                 else '1900'),
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
    Build a dictionary for a FillerItem using a PlexAPI Video, Movie or Episode object
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


def get_non_shows(media_items: List) -> List:
    """
    Get all non_show items
    :param media_items: list of MediaItem objects
    :return: list of non-show MediaItem objects
    """
    return [item for item in media_items if
            ((_object_has_attribute(object=item, attribute_name='type') and item.type != 'episode') or
             (_object_has_attribute(object=item, attribute_name='season') and not item.season))]


def make_show_dict(media_items: List) -> dict:
    """
    Convert a list of MediaItem objects into a show-season-episode dictionary
    Disregards any non-episode media items
    :param media_items: list of MediaItem objects
    :return: dict object with all episodes arranged by show-season-episode
    """
    show_dict = {}
    for item in media_items:
        if _object_has_attribute(object=item, attribute_name='type') and item.type == 'episode' and item.episode:
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


def add_durations_to_show_dict(show_dict: dict) -> dict:
    """
    Add episode, season and show duration to show_dict
    :param show_dict: dictionary of shows in show-season-episode structure
    :return: dict object with duration included for each episode, season and show
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
    :return: dict object with all episodes arranged by show-episode
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


def datetime_to_string(datetime_object: datetime, template: str = "%Y-%m-%dT%H:%M:%S.000Z") -> str:
    """
    Convert a datetime.datetime object to a string
    :param datetime_object: datetime.datetime object to convert
    :param template: (Optional) datetime template to use when parsing string
    :return: str representation of datetime
    """
    return datetime_object.strftime(template)


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


# Sorting
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


def sort_media_alphabetically(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Sort media items alphabetically.
    Note: Shows will be grouped and sorted by series title, but episodes may be out of order
    :param media_items: List of Program and FillerItem objects
    :return: List of Program and FillerItem objects
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
    :return: List of Program and FillerItem objects
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
    :return: List of Program and FillerItem objects
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
    :return: List of Program and FillerItem objects
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
    :return: List of Program and FillerItem objects
    """
    non_redirects = [item for item in media_items if
                     (_object_has_attribute(object=item, attribute_name='duration')
                      and _object_has_attribute(object=item, attribute_name='type')
                      and item.type != 'redirect')]
    sorted_media = sorted(non_redirects, key=lambda x: x.duration)
    return sorted_media


def sort_media_randomly(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Sort media randomly.
    :param media_items: List of Program and FillerItem objects
    :return: List of Program and FillerItem objects
    """
    shuffle(items=media_items)
    return media_items


def sort_media_cyclical_shuffle(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Sort media cyclically.
    Note: Automatically removes FillerItem objects
    :param media_items: List of Program and FillerItem objects
    :return: List of Program objects, FillerItem objects removed
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
    categories = ['show', 'non_show']
    while len(final_list) != total_item_count:
        if 'non_show' in categories and len(non_shows) == 0:
            categories.remove('non_show')
        if 'show' in categories and show_list['remaining_episode_count'] == 0:
            categories.remove('show')
        if not categories:
            break
        show_or_non_show = random_choice(items=categories)
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
    :param block_length: length of each block of programming
    :param randomize: random length (up to block_length) and random order
    :return: List of Program objects, FillerItem objects removed
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
    :param margin_of_correction: Percentage over shortest time to use when assessing whether to add a new episode
    :return: List of Program and FillerItem objects
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
    print(ordered_show_dict_with_durations)
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


def remove_duplicate_media_items(media_items: List[Union[Program, FillerItem]]) -> List[Union[Program, FillerItem]]:
    """
    Remove duplicate items from list of media items.
    Check by ratingKey.
    Note: Automatically removes redirect items
    :param media_items: List of Program and FillerItem objects
    :return: List of Program and FillerItem objects
    """
    non_redirects = [item for item in media_items if
                     (_object_has_attribute(object=item, attribute_name='type')
                      and item.type != 'redirect')]
    return remove_duplicates_by_attribute(items=non_redirects, attribute_name='ratingKey')


def _get_first_x_minutes_of_programs(programs: List[Union[Program, Redirect, FillerItem]],
                                     minutes: int) -> Tuple[List[Union[Program, Redirect, FillerItem]], int]:
    """
    Keep building a list of programs in order until a duration limit is met.
    :param programs: list of Program objects to pull from
    :param minutes: threshold, in minutes
    :return: list of Program objects, total running time in milliseconds
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
    :param minutes: threshold, in minutes
    :return: list of Program objects, total running time in milliseconds, unused Programs
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
