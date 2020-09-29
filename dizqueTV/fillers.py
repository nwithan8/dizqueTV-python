import json
from typing import List, Union
from datetime import datetime, timedelta

from plexapi.video import Video, Movie, Episode
from plexapi.server import PlexServer as PServer

import dizqueTV.helpers as helpers
from dizqueTV.media import FillerItem
from dizqueTV.templates import FILLER_ITEM_TEMPLATE
from dizqueTV.exceptions import MissingParametersError


class FillerList:
    def __init__(self, data: json, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self.id = data.get('id')
        self.name = data.get('name')
        self.count = data.get('count')
        self._filler_data = data.get('content')
        if not self.count and self._filler_data:
            self.count = len(self._filler_data)

    # CRUD Operations
    # Create (handled in dizqueTV.py)
    # Read
    @helpers._check_for_dizque_instance
    def refresh(self):
        """
        Reload current FillerList object
        Use to update filler data
        """
        temp_filler_list = self._dizque_instance.get_filler_list(filler_list_id=self.id)
        if temp_filler_list:
            print(temp_filler_list)
            json_data = temp_filler_list._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_filler_list

    @property
    @helpers._check_for_dizque_instance
    def details(self) -> json:
        return self._dizque_instance.get_filler_list_info(filler_list_id=self.id)

    @property
    def content(self) -> List[FillerItem]:
        """
        Get all filler items on this list
        :return: List of FillerItem objects
        """
        if not self._filler_data:
            self.refresh()
        return [FillerItem(data=filler, dizque_instance=self._dizque_instance, filler_list_instance=self)
                for filler in self._filler_data]

    @property
    @helpers._check_for_dizque_instance
    def channels(self) -> List:
        """
        Get all channels this filler list is used on
        :return: List of Channel objects
        """
        return self._dizque_instance.get_filler_list_channels(filler_list_id=self.id)

    # Update
    @helpers._check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit this FillerList on dizqueTV
        Automatically refreshes current FillerList object
        :param kwargs: keyword arguments of FillerList settings names and values
        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        """
        if self._dizque_instance.update_filler_list(filler_list_id=self.id, **kwargs):
            self.refresh()
            return True
        return False

    @helpers._check_for_dizque_instance
    def add_filler(self,
                   plex_item: Union[Video, Movie, Episode] = None,
                   plex_server: PServer = None,
                   filler: FillerItem = None, **kwargs) -> bool:
        """
        Add a filler item to this filler list
        :param plex_item: plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode object (optional)
        :param plex_server: plexapi.server.PlexServer object (optional)
        :param filler: FillerItem item (optional)
        :param kwargs: keyword arguments of FillerItem settings names and values
        :return: True if successful, False if unsuccessful (FillerList reloads in place)
        """
        if not plex_item and not filler and not kwargs:
            raise MissingParametersError("Please include either a program, a plex_item/plex_server combo, or kwargs")
        if plex_item and plex_server:
            temp_filler = self._dizque_instance.convert_plex_item_to_filler(plex_item=plex_item,
                                                                            plex_server=plex_server)
            kwargs = temp_filler._data
        if filler:
            kwargs = filler._data
        if helpers._settings_are_complete(new_settings_dict=kwargs,
                                          template_settings_dict=FILLER_ITEM_TEMPLATE,
                                          ignore_id=True):
            filler_list_data = self._data
            filler_list_data['content'].append(kwargs)
            filler_list_data['duration'] += kwargs['duration']
            return self.update(**filler_list_data)
        return False

    @helpers._check_for_dizque_instance
    def add_fillers(self,
                    fillers: List[Union[FillerItem, Video, Movie, Episode]],
                    plex_server: PServer = None) -> bool:
        """
        Add multiple programs to this channel
        :param fillers: List of FillerItem, plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode objects
        :param plex_server: plexapi.server.PlexServer object
        (required if adding PlexAPI Video, Movie or Episode objects)
        :return: True if successful, False if unsuccessful (Channel reloads in place)
        """
        filler_list_data = self._data
        for filler in fillers:
            if type(filler) != FillerItem:
                if not plex_server:
                    raise MissingParametersError("Please include a plex_server if you are adding PlexAPI Video, "
                                                 "Movie, or Episode items.")
                filler = self._dizque_instance.convert_plex_item_to_filler(plex_item=filler, plex_server=plex_server)
            filler_list_data['content'].append(filler._data)
            filler_list_data['duration'] += filler.duration
        return self.update(**filler_list_data)

    @helpers._check_for_dizque_instance
    def delete_filler(self, filler: FillerItem) -> bool:
        """
        Delete a filler item from this filler list
        :param filler: FillerItem object to delete
        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        """
        filler_list_data = self._data
        for a_filler in filler_list_data['content']:
            if a_filler['title'] == filler.title:
                filler_list_data['duration'] -= a_filler['duration']
                filler_list_data['content'].remove(a_filler)
                return self.update(**filler_list_data)
        return False

    @helpers._check_for_dizque_instance
    def delete_all_fillers(self) -> bool:
        """
        Delete all filler items from this filler list
        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        """
        filler_list_data = self._data
        filler_list_data['duration'] -= sum(filler.duration for filler in self.content)
        filler_list_data['content'] = []
        return self.update(**filler_list_data)

    # Sort FillerItem
    @helpers._check_for_dizque_instance
    def sort_filler_by_duration(self) -> bool:
        """
        Sort all filler items on this filler list by duration
        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        """
        sorted_filler = helpers.sort_media_by_duration(media_items=self.content)
        if sorted_filler and self.delete_all_fillers():
            return self.add_fillers(fillers=sorted_filler)
        return False

    @helpers._check_for_dizque_instance
    def sort_filler_randomly(self) -> bool:
        """
        Sort all filler items on this filler list randomly
        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        """
        sorted_filler = helpers.sort_media_randomly(media_items=self.content)
        if sorted_filler and self.delete_all_fillers():
            return self.add_fillers(fillers=sorted_filler)
        return False

    @helpers._check_for_dizque_instance
    def remove_duplicate_fillers(self) -> bool:
        """
        Delete duplicate filler items on this filler list
        :return: True if successful, False if unsuccessful (FillerList reloads in-place)
        """
        sorted_filler = helpers.remove_duplicate_media_items(media_items=self.content)
        if sorted_filler and self.delete_all_fillers():
            return self.add_fillers(fillers=sorted_filler)
        return False

    # Delete
    @helpers._check_for_dizque_instance
    def delete(self) -> bool:
        """
        Delete this filler list
        :return: True if successful, False if unsuccessful
        """
        # delete from all channels first
        for channel in self.channels:
            channel.delete_filler_list(filler_list=self)
        return self._dizque_instance.delete_filler_list(filler_list_id=self.id)

