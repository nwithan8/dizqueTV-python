class BaseObject:
    def __init__(self, data: dict):
        self._data = data

    @property
    def json(self) -> dict:
        """
        Get raw JSON

        :return: JSON data for object
        :rtype: dict
        """
        return self._data

class BaseAPIObject(BaseObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data)
        self._dizque_instance = dizque_instance