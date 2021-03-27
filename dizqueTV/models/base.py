class BaseObject:
    def __init__(self, data: dict):
        self._raw_data = data

    @property
    def json(self) -> dict:
        """
        Get raw JSON

        :return: JSON data for object
        :rtype: dict
        """
        return self._raw_data

    @property
    def _data(self) -> dict:
        """
        Get raw JSON

        :return: JSON data for object
        :rtype: dict
        """
        return self._raw_data

class BaseAPIObject(BaseObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data)
        self._dizque_instance = dizque_instance