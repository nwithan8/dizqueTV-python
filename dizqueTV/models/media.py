import dizqueTV.decorators as decorators
from dizqueTV.exceptions import MissingParametersError
from dizqueTV.models.base import BaseAPIObject


class BaseMediaItem(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance, channel_instance=None):
        super().__init__(data, dizque_instance)
        self.type = data.get('type')
        self.isOffline = data.get('isOffline')
        self.duration = data.get('duration')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type})"


class MediaItem(BaseMediaItem):
    def __init__(self, data: dict, dizque_instance, channel_instance=None):
        super().__init__(data=data, dizque_instance=dizque_instance, channel_instance=channel_instance)
        self.title = data.get('title')
        self.key = data.get('key')
        self.ratingKey = data.get('ratingKey')
        self.duration = data.get('duration')
        self.icon = data.get('icon')
        self.summary = data.get('summary')
        self.date = data.get('date')
        self.year = data.get('year')
        self.plexFile = data.get('plexFile')
        self.file = data.get('file')
        self.showTitle = data.get('showTitle')
        self.episode = data.get('episode')
        self.season = data.get('season')
        self.serverKey = data.get('serverKey')

        self.showIcon = data.get('showIcon')
        self.episodeIcon = data.get('episodeIcon')
        self.seasonIcon = data.get('seasonIcon')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title})"


class Redirect(BaseMediaItem):
    def __init__(self, data: dict, dizque_instance, channel_instance):
        super().__init__(data=data, dizque_instance=dizque_instance)
        self._channel_instance = channel_instance
        self.channel = data.get('channel')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.channel})"


class Program(MediaItem, Redirect):
    def __init__(self, data: dict, dizque_instance, channel_instance):
        super().__init__(data=data, dizque_instance=dizque_instance, channel_instance=channel_instance)
        self.rating = data.get('rating')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title})"

    @decorators.check_for_dizque_instance
    def refresh(self, data: dict = None, program_title: str = None, redirect_channel_number: int = None):
        """
        Reload current Program object
        Use to update data

        :return: None
        """
        if not data and not program_title and not redirect_channel_number:
            raise MissingParametersError("Please include either a JSON array, program_title or a redirect_channel_number.")
        if program_title or redirect_channel_number:
            temp_program = self._channel_instance.get_program(program_title = program_title, redirect_channel_number = redirect_channel_number)
            if not temp_program:
                raise Exception("Could not find program.")
            else:
                data = temp_program._data
                self._channel_instance = temp_program._channel_instance,
                self._dizque_instance = temp_program._dizque_instance
                del temp_program
        self.__init__(data=data, channel_instance=self._channel_instance, dizque_instance=self._dizque_instance)


    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Update this program

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        return self._channel_instance.update_program(program=self, **kwargs)


    @decorators.check_for_dizque_instance
    def delete(self) -> bool:
        """
        Delete this program

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        return self._channel_instance.delete_program(program=self)


class FillerItem(MediaItem):
    def __init__(self, data: dict, dizque_instance, filler_list_instance):
        super().__init__(data=data, dizque_instance=dizque_instance)
        self._filler_list_instance = filler_list_instance

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title})"

    @decorators.check_for_dizque_instance
    def refresh(self, data: dict = None, filler_item_title: str = None):
        """
        Reload current FillerItem object
        Use to update data

        :return: None
        """
        if not data and not filler_item_title:
            raise MissingParametersError(
                "Please include either a JSON array or a filler_item_title.")
        if filler_item_title:
            temp_item = self._filler_list_instance.get_filler_item(filler_item_title=filler_item_title)
            if not temp_item:
                raise Exception("Could not find filler item.")
            else:
                data = temp_item._data
                self._filler_list_instance = temp_item._filler_list_instance,
                self._dizque_instance = temp_item._dizque_instance
                del temp_item
        self.__init__(data=data, filler_list_instance=self._filler_list_instance, dizque_instance=self._dizque_instance)

    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Update this filler

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        return self._filler_list_instance.update_filler(program=self, **kwargs)

    @decorators.check_for_dizque_instance
    def delete(self) -> bool:
        """
        Delete this filler

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        return self._filler_list_instance.delete_filler(filler=self)
