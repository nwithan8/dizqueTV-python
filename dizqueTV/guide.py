import json
from typing import Union, List
from datetime import datetime

import dizqueTV.helpers as helpers


class GuideProgram:
    def __init__(self, data):
        self._data = data
        self.start = data.get('start')
        self.stop = data.get('stop')
        self.summary = data.get('summary')
        self.date = data.get('date')
        self.rating = data.get('rating')
        self.icon = data.get('icon')
        self.title = data.get('title')


class GuideChannel:
    def __init__(self, data, programs, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self.name = data.get('name')
        self.icon = data.get('icon')
        self.number = data.get('number')
        self.programs = programs

    def get_lineup(self, from_date: datetime, to_date: datetime) -> List[GuideProgram]:
        """
        Get guide channel lineup for a certain time range
        :param from_date: datetime.datetime object to start time frame
        :param to_date: datetime.datetime object to end time frame
        :return: list of GuideProgram objects
        """
        params = {
            'dateFrom': helpers.datetime_to_string(datetime_object=from_date),
            'dateTo': helpers.datetime_to_string(datetime_object=to_date)
        }
        json_data = self._dizque_instance._get_json(endpoint=f'/guide/channels/{self.number}', params=params)
        if json_data.get('programs'):
            return [GuideProgram(data=program_data) for program_data in json_data['programs']]
        return []


class Guide:
    def __init__(self, data, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self.channels = self._create_channels_and_programs()

    def _create_channels_and_programs(self):
        channels = []
        for channel_number, data in self._data.items():
            programs = [GuideProgram(data=program_data) for program_data in data['programs']]
            channel = GuideChannel(data=data['channel'], programs=programs, dizque_instance=self._dizque_instance)
            channels.append(channel)
        return channels

    @property
    def last_update(self) -> Union[datetime, None]:
        """
        Get the last update time for the guide
        :return: datetime.datetime object
        """
        data = self._dizque_instance._get_json(endpoint='/guide/status')
        if data and data.get('lastUpdate'):
            return helpers.string_to_datetime(date_string=data['lastUpdate'])
        return None
