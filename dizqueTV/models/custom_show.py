from dizqueTV.models.base import BaseObject, BaseAPIObject

class CustomShowItem(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

class CustomShowDetails(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)
        self.name = data.get('name')

class CustomShow(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.id = data.get('id')
        self.name = data.get('name')
        self.count = data.get('count')
        self._details = None

    @property
    def details(self):
        if not self._details:
            self._details = self._dizque_instance.get_custom_show_details(custom_show_id=self.id)
        return self._details


