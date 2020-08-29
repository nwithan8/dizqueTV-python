import json

import dizqueTV.helpers as helpers


class PlexServer:
    def __init__(self, data: json, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self.name = data.get('name')
        self.uri = data.get('uri')
        self.accessToken = data.get('accessToken')
        self.index = data.get('index')
        self.arChannels = data.get('arChannels')
        self.arGuide = data.get('arGuide')
        self._id = data.get('_id')

    @property
    @helpers._check_for_dizque_instance
    def status(self) -> bool:
        """
        Check if this Plex Media Server is accessible
        :return: True if active, False if not active
        """
        return self._dizque_instance.plex_server_status(server_name=self.name)

    @property
    @helpers._check_for_dizque_instance
    def foreign_status(self) -> bool:
        """

        :return: True if active, False if not active
        """
        return self._dizque_instance.plex_server_foreign_status(server_name=self.name)

    @helpers._check_for_dizque_instance
    def refresh(self):
        """
        Reload this Plex Media Server
        """
        if self._dizque_instance:
            temp_server = self._dizque_instance.get_plex_server(server_name=self.name)
            if temp_server:
                json_data = temp_server._data
                self.__init__(data=json_data, dizque_instance=self._dizque_instance)
                del temp_server

    @helpers._check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit this Plex Media Server on dizqueTV
        Automatically refreshes current PlexServer object
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance:
            if self._dizque_instance.update_plex_server(server_name=self.name, **kwargs):
                self.refresh()
                return True
        return False

    @helpers._check_for_dizque_instance
    def delete(self) -> bool:
        """
        Remove this Plex Media Server from dizqueTV
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance:
            return self._dizque_instance.delete_plex_server(server_name=self.name)
        return False
