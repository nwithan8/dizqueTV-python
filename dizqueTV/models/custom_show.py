from typing import Union, List

from dizqueTV.models.media import Program

from dizqueTV.models.base import BaseAPIObject


class CustomShowItem(Program):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance, None)
        self._full_data = data
        self.durationStr = data.get('durationStr')
        self._commercials = []

    @property
    def _data(self):
        """
        Override default self._data to ignore durationStr and commercials

        :return: Data dict
        :rtype: dict
        """
        data = self._full_data
        data.pop('durationStr', None)
        data.pop('commercials', None)
        return data

    @property
    def commercials(self) -> List:
        """
        Get the show's commercials

        :return: List of commercials
        :rtype: list
        """
        if not self._commercials:
            self._commercials = []
        return self._commercials


class CustomShowDetails(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.name = data.get('name')
        self.id = data.get('id')
        self._content = []

    @property
    def content(self) -> List[CustomShowItem]:
        """
        Get the custom show's content (the actual programs)

        :return: list of CustomShowItem objects
        :rtype: list
        """
        if not self._content:
            self._content = [CustomShowItem(item_data, self._dizque_instance) for item_data in
                             self._data.get('content', [])]
        return self._content


class CustomShow(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.id = data.get('id')
        self.name = data.get('name')
        self.count = data.get('count')
        self.customShowTag = "customShow"
        self._details = None

    @property
    def details(self) -> Union[CustomShowDetails, None]:
        """
        Get the custom show's details

        :return: CustomShowDetails object
        :rtype: CustomShowDetails
        """
        if not self._details:
            self._details = self._dizque_instance.get_custom_show_details(custom_show_id=self.id)
        return self._details

    @property
    def content(self):
        """
        Get the custom show's content (the actual programs)

        :return: list of CustomShowItem objects
        :rtype: list
        """
        details = self.details
        if not details:
            return []
        return details.content
