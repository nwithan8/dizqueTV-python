class BaseAPIObject:
    def __init__(self, data: dict, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance