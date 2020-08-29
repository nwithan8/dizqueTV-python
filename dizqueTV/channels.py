import json
from typing import List, Union

import dizqueTV.helpers as helpers
from dizqueTV.templates import PROGRAM_ITEM_TEMPLATE, FILLER_ITEM_TEMPLATE


class MediaItem:
    def __init__(self, data: json, dizque_instance, channel_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self._channel_instance = channel_instance
        self.title = data.get('title')
        self.key = data.get('key')
        self.ratingKey = data.get('ratingKey')
        self.icon = data.get('icon')
        self.type = data.get('type')
        self.duration = data.get('duration')
        self.summary = data.get('summary')
        self.date = data.get('date')
        self.year = data.get('year')
        self.plexFile = data.get('plexFile')
        self.file = data.get('file')
        self.showTitle = data.get('showTitle')
        self.episode = data.get('episode')
        self.season = data.get('season')
        self.serverKey = data.get('serverKey')
        self.isOffline = data.get('isOffline')

        self.showIcon = data.get('showIcon')
        self.episodeIcon = data.get('episodeIcon')
        self.seasonIcon = data.get('seasonIcon')


class Filler(MediaItem):
    def __init__(self, data: json, dizque_instance, channel_instance):
        super().__init__(data=data, dizque_instance=dizque_instance, channel_instance=channel_instance)

    def delete(self) -> bool:
        """
        Delete this filler
        :return: True if successful, False if unsuccessful
        """
        if self._channel_instance:
            return self._channel_instance.delete_filler(filler=self)
        return False


class Program(MediaItem):
    def __init__(self, data: json, dizque_instance, channel_instance):
        super().__init__(data=data, dizque_instance=dizque_instance, channel_instance=channel_instance)
        self.rating = data.get('rating')

    def delete(self) -> bool:
        """
        Delete this program
        :return: True if successful, False if unsuccessful
        """
        if self._channel_instance:
            return self._channel_instance.delete_program(program=self)
        return False


class Channel:
    def __init__(self, data: json, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self._program_data = data.get('programs')
        self._fillerContent_data = data.get('fillerContent')
        self.fillerRepeatCooldown = data.get('fillerRepeatCooldown')
        self.fallback = data.get('fallback')
        self.icon = data.get('icon')
        self.disableFillerOverlay = data.get('disableFillerOverlay')
        self.iconWidth = data.get('iconWidth')
        self.iconDuration = data.get('iconDuration')
        self.iconPosition = data.get('iconPosition')
        self.overlayIcon = data.get('overlayIcon')
        self.startTime = data.get('startTime')
        self.offlinePicture = data.get('offlinePicture')
        self.offlineSoundtrack = data.get('offlineSoundtrack')
        self.offlineMode = data.get('offlineMode')
        self.number = data.get('number')
        self.name = data.get('name')
        self.duration = data.get('duration')
        self._id = data.get('_id')

    @property
    def programs(self):
        """
        Get all programs on this channel
        :return: List of MediaItem objects
        """
        return [Program(data=program, dizque_instance=self._dizque_instance, channel_instance=self)
                for program in self._program_data]

    def get_program(self, program_title: str) -> Union[Program, None]:
        """
        Get a specific program on this channel
        :param program_title: Title of program
        :return: Program object or None
        """
        for program in self.programs:
            if program.title == program_title:
                return program
        return None

    @property
    def filler(self):
        """
        Get all filler (Flex) items on this channel
        :return: List of MediaItem objects
        """
        return [Filler(data=filler, dizque_instance=self._dizque_instance, channel_instance=self)
                for filler in self._fillerContent_data]

    def get_filler(self, filler_title: str) -> Union[Filler, None]:
        """
        Get a specific filler item on this channel
        :param filler_title: Title of filler item
        :return: Filler object or None
        """
        for filler in self.filler:
            if filler.title == filler_title:
                return filler
        return None

    def refresh(self):
        """
        Reload current Channel object
        Use to update program and filler data
        """
        temp_channel = self._dizque_instance.get_channel(channel_number=self.number)
        if temp_channel:
            json_data = temp_channel._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_channel

    def update(self, **kwargs) -> bool:
        """
        Edit this Channel on dizqueTV
        Automatically refreshes current Channel object
        :param kwargs: keyword arguments of Channel settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        if self._dizque_instance.update_channel(channel_number=self.number, **kwargs):
            self.refresh()
            return True
        return False

    def delete(self) -> bool:
        """
        Delete this channel
        :return: True if successful, False if unsuccessful
        """
        return self._dizque_instance.delete_channel(channel_number=self.number)

    def add_program(self, program: Program = None, **kwargs) -> bool:
        """
        Add a program to this channel
        :param program: Program item (optional)
        :param kwargs: keyword arguments of Program settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in place)
        """
        if program:
            kwargs = program._data
        if helpers.settings_are_complete(new_settings_dict=kwargs,
                                         template_settings_dict=PROGRAM_ITEM_TEMPLATE,
                                         ignore_id=True):
            channel_data = self._data
            channel_data['programs'].append(kwargs)
            channel_data['duration'] += kwargs['duration']
            return self.update(**channel_data)
        return False

    def delete_program(self, program: Program) -> bool:
        """
        Delete a program from this channel
        :param program: Program object to delete
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        channel_data = self._data
        for a_program in channel_data['programs']:
            if a_program['title'] == program.title:
                channel_data['duration'] -= a_program['duration']
                channel_data['programs'].remove(a_program)
                return self.update(**channel_data)
        return False

    def add_filler(self, filler: Filler = None, **kwargs) -> bool:
        """
        Add a filler item to this channel
        :param filler: Filler item (optional)
        :param kwargs: keyword arguments of Filler settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in place)
        """
        if filler:
            kwargs = filler._data
        if helpers.settings_are_complete(new_settings_dict=kwargs,
                                         template_settings_dict=FILLER_ITEM_TEMPLATE,
                                         ignore_id=True):
            channel_data = self._data
            channel_data['programs'].append(kwargs)
            channel_data['duration'] += kwargs['duration']
            return self.update(**channel_data)
        return False

    def delete_filler(self, filler: Filler) -> bool:
        """
        Delete a filler item from this channel
        :param filler: Filler object to delete
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        channel_data = self._data
        for a_filler in channel_data['filler']:
            if a_filler['title'] == filler.title:
                channel_data['duration'] -= a_filler['duration']
                channel_data['filler'].remove(a_filler)
                return self.update(**channel_data)
        return False