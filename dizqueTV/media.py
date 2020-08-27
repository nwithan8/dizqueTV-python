import json


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
        return [MediaItem(data=program, dizque_instance=self._dizque_instance) for program in self._program_data]

    @property
    def filler(self):
        """
        Get all filler (Flex) items on this channel
        :return: List of MediaItem objects
        """
        return [MediaItem(data=filler, dizque_instance=self._dizque_instance) for filler in self._fillerContent_data]

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
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
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


class MediaItem:
    def __init__(self, data: json, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self.title = data.get('title')
        self.key = data.get('key')
        self.ratingKey = data.get('ratingKey')
        self.icon = data.get('icon')
        self.type = data.get('type')
        self.duration = data.get('duration')
        self.summary = data.get('summary')
        self.rating = data.get('rating')
        self.data = data.get('date')
        self.year = data.get('year')
        self.plexFile = data.get('plexFile')
        self.file = data.get('file')
        self.showTitle = data.get('showTitle')
        self.episode = data.get('episode')
        self.season = data.get('season')
        self.serverKey = data.get('serverKey')
        self.isOffline = data.get('isOffline')
