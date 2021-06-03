from dizqueTV import decorators
from dizqueTV.models.base import BaseAPIObject


class PlexServer(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.name = data.get('name')
        self.uri = data.get('uri')
        self.accessToken = data.get('accessToken')
        self.index = data.get('index')
        self.arChannels = data.get('arChannels')
        self.arGuide = data.get('arGuide')
        self._id = data.get('_id')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    @property
    @decorators.check_for_dizque_instance
    def status(self) -> bool:
        """
        Check if this Plex Media Server is accessible

        :return: True if active, False if not active
        :rtype: bool
        """
        return self._dizque_instance.plex_server_status(server_name=self.name)

    @property
    @decorators.check_for_dizque_instance
    def foreign_status(self) -> bool:
        """

        :return: True if active, False if not active
        :rtype: bool
        """
        return self._dizque_instance.plex_server_foreign_status(server_name=self.name)

    @decorators.check_for_dizque_instance
    def refresh(self):
        """
        Reload this Plex Media Server

        :return: None
        :rtype: None
        """
        if self._dizque_instance:
            temp_server = self._dizque_instance.get_plex_server(server_name=self.name)
            if temp_server:
                json_data = temp_server._data
                self.__init__(data=json_data, dizque_instance=self._dizque_instance)
                del temp_server

    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit this Plex Media Server on dizqueTV
        Automatically refreshes current PlexServer object

        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance:
            if self._dizque_instance.update_plex_server(server_name=self.name, **kwargs):
                self.refresh()
                return True
        return False

    @decorators.check_for_dizque_instance
    def delete(self) -> bool:
        """
        Remove this Plex Media Server from dizqueTV

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance:
            return self._dizque_instance.delete_plex_server(server_name=self.name)
        return False
