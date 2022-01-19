from typing import List, Union

from plexapi.audio import Track
from plexapi.server import PlexServer as PServer
from plexapi.video import Video, Movie, Episode

import dizqueTV.helpers as helpers
from dizqueTV import decorators
from dizqueTV.exceptions import MissingParametersError
from dizqueTV.models.base import BaseAPIObject
from dizqueTV.models.custom_show import CustomShow, CustomShowItem
from dizqueTV.models.media import FillerItem
from dizqueTV.models.templates import FILLER_ITEM_TEMPLATE


class FillerList(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.id = data.get('id')
        self.name = data.get('name')
        self.count = data.get('count')
        self._filler_data = data.get('content')
        if not self.count and self._filler_data:
            self.count = len(self._filler_data)

    # CRUD Operations
    # Create (handled in dizqueTV.py)
    # Read
    @decorators.check_for_dizque_instance
    def refresh(self):
        """
        Reload current FillerList object
        Use to update filler data

        :return: None
        :rtype: None
        """
        temp_filler_list = self._dizque_instance.get_filler_list(filler_list_id=self.id)
        if temp_filler_list:
            print(temp_filler_list)
            json_data = temp_filler_list._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_filler_list

    @property
    @decorators.check_for_dizque_instance
    def details(self) -> dict:
        """
        Get FillerList JSON

        :return: JSON data for FillerList object
        :rtype: dict
        """
        return self._dizque_instance.get_filler_list_info(filler_list_id=self.id)

    @property
    def content(self) -> List[Union[FillerItem, CustomShow]]:
        """
        Get all filler items on this list

        :return: List of FillerItem and CustomShow objects
        :rtype: List[Union[FillerItem, CustomShow]]
        """
        if not self._filler_data:
            self.refresh()
        return self._dizque_instance.parse_custom_shows_and_non_custom_shows(items=self._filler_data,
                                                                             non_custom_show_type=FillerItem,
                                                                             dizque_instance=self._dizque_instance,
                                                                             filler_list_instance=self)

    @property
    @decorators.check_for_dizque_instance
    def channels(self) -> List:
        """
        Get all channels this filler list is used on

        :return: List of Channel objects
        :rtype: List[Channel]
        """
        return self._dizque_instance.get_filler_list_channels(filler_list_id=self.id)

    # Update
    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit this FillerList on dizqueTV
        Automatically refreshes current FillerList object

        :param kwargs: keyword arguments of FillerList settings names and values
        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        :rtype: bool
        """
        if self._dizque_instance.update_filler_list(filler_list_id=self.id, **kwargs):
            self.refresh()
            return True
        return False

    @decorators.check_for_dizque_instance
    def get_filler_item(self,
                        filler_item_title: str) -> Union[FillerItem, None]:
        """
        Get a specific program on this channel

        :param filler_item_title: Title of filler item
        :type filler_item_title: str, optional
        :return: FillerItem object or None
        :rtype: FillerItem
        """
        for filler_item in self.content:
            if filler_item_title == filler_item_title:
                return filler_item
        return None

    @decorators.check_for_dizque_instance
    def add_filler(self,
                   plex_item: Union[Video, Movie, Episode, Track] = None,
                   plex_server: PServer = None,
                   filler: FillerItem = None,
                   **kwargs) -> bool:
        """
        Add a filler item to this filler list

        :param plex_item: plexapi.video.Video, plexapi.video.Moviem plexapi.video.Episode or plexapi.audio.Track object (optional)
        :type plex_item: Union[plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode, plexapi.audio.Track], optional
        :param plex_server: plexapi.server.PlexServer object (optional)
        :type plex_server: plexapi.server.PlexServer, optional
        :param filler: FillerItem item (optional)
        :type filler: FillerItem, optional
        :param kwargs: keyword arguments of FillerItem settings names and values
        :return: True if successful, False if unsuccessful (FillerList reloads in place)
        :rtype: bool
        """
        if not plex_item and not filler and not kwargs:
            raise MissingParametersError("Please include either a program, a plex_item/plex_server combo, or kwargs")
        if plex_item and plex_server:
            temp_filler = self._dizque_instance.convert_plex_item_to_filler(plex_item=plex_item,
                                                                            plex_server=plex_server)
            kwargs = temp_filler._data
        if filler:
            if type(filler) == CustomShow:
                # pass CustomShow handling to add_programs, since multiple programs need to be added
                return self.add_fillers(fillers=[filler])
            kwargs = filler._data
        if helpers._settings_are_complete(new_settings_dict=kwargs,
                                             template_settings_dict=FILLER_ITEM_TEMPLATE,
                                             ignore_keys=['_id', 'id']):
            filler_list_data = self._data
            filler_list_data['content'].append(kwargs)
            if filler_list_data.get('duration'):
                filler_list_data['duration'] += kwargs['duration']
            return self.update(**filler_list_data)
        return False

    @decorators.check_for_dizque_instance
    def add_fillers(self,
                    fillers: List[Union[FillerItem, CustomShow, Video, Movie, Episode, Track]],
                    plex_server: PServer = None) -> bool:
        """
        Add multiple programs to this channel

        :param fillers: List of FillerItem, CustomShow, plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode or plexapi.audio.Track objects
        :type fillers: List[Union[FillerItem, CustomShow, plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode, plexapi.audio.Track]]
        :param plex_server: plexapi.server.PlexServer object (required if adding PlexAPI Video, Movie, Episode or Track objects)
        :type plex_server: plexapi.server.PlexServer, optional
        :return: True if successful, False if unsuccessful (Channel reloads in place)
        :rtype: bool
        """
        filler_list_data = self._data

        fillers = self._dizque_instance.expand_custom_show_items(programs=fillers, dizque_instance=self)

        for filler in fillers:
            if type(filler) not in [FillerItem, CustomShowItem]:
                if not plex_server:
                    raise MissingParametersError("Please include a plex_server if you are adding PlexAPI Video, "
                                                 "Movie, Episode or Track items.")
                filler = self._dizque_instance.convert_plex_item_to_filler(plex_item=filler, plex_server=plex_server)
            filler_list_data['content'].append(filler._data)
            if filler_list_data.get('duration'):
                filler_list_data['duration'] += filler.duration
        return self.update(**filler_list_data)

    @decorators.check_for_dizque_instance
    def update_filler(self, filler: FillerItem, **kwargs) -> bool:
        """
        Update a filler item on this filler list

        :param filler: FillerItem object to update
        :type filler: FillerItem
        :param kwargs: Keyword arguments of new FillerItem settings names and values
        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        :rtype: bool
        """
        filler_list_data = self._data
        for a_filler in filler_list_data['content']:
            if a_filler['title'] == filler.title:
                if kwargs.get('duration'):
                    filler_list_data['duration'] -= a_filler['duration']
                    filler_list_data['duration'] += kwargs['duration']
                new_data = helpers._combine_settings(new_settings_dict=kwargs, default_dict=a_filler)
                a_filler.update(new_data)
                return self.update(**filler_list_data)
        return False

    @decorators.check_for_dizque_instance
    def delete_filler(self, filler: FillerItem) -> bool:
        """
        Delete a filler item from this filler list

        :param filler: FillerItem object to delete
        :type filler: FillerItem
        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        :rtype: bool
        """
        filler_list_data = self._data
        for a_filler in filler_list_data['content']:
            if a_filler['title'] == filler.title:
                if filler_list_data.get('duration'):
                    filler_list_data['duration'] -= a_filler['duration']
                filler_list_data['content'].remove(a_filler)
                return self.update(**filler_list_data)
        return False

    @decorators.check_for_dizque_instance
    def delete_all_fillers(self) -> bool:
        """
        Delete all filler items from this filler list

        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        :rtype: bool
        """
        filler_list_data = self._data
        if filler_list_data.get('duration'):
            filler_list_data['duration'] -= sum(filler.duration for filler in self.content)
        filler_list_data['content'] = []
        return self.update(**filler_list_data)

    # Sort FillerItem
    @decorators.check_for_dizque_instance
    def sort_filler_by_duration(self) -> bool:
        """
        Sort all filler items on this filler list by duration

        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        :rtype: bool
        """
        sorted_filler = helpers.sort_media_by_duration(media_items=self.content)
        if sorted_filler and self.delete_all_fillers():
            return self.add_fillers(fillers=sorted_filler)
        return False

    @decorators.check_for_dizque_instance
    def sort_filler_randomly(self) -> bool:
        """
        Sort all filler items on this filler list randomly

        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        :rtype: bool
        """
        sorted_filler = helpers.sort_media_randomly(media_items=self.content)
        if sorted_filler and self.delete_all_fillers():
            return self.add_fillers(fillers=sorted_filler)
        return False

    @decorators.check_for_dizque_instance
    def remove_duplicate_fillers(self) -> bool:
        """
        Delete duplicate filler items on this filler list

        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        :rtype: bool
        """
        sorted_filler = helpers.remove_duplicate_media_items(media_items=self.content)
        if sorted_filler and self.delete_all_fillers():
            return self.add_fillers(fillers=sorted_filler)
        return False

    # Delete
    @decorators.check_for_dizque_instance
    def delete(self) -> bool:
        """
        Delete this filler list

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        # delete from all channels first
        for channel in self.channels:
            channel.delete_filler_list(filler_list=self)
        return self._dizque_instance.delete_filler_list(filler_list_id=self.id)
