from typing import List

from requests import Response

import dizqueTV.dizquetv_requests as requests

class Advanced:
    def __init__(self, dizque_instance):
        self._dizque_instance = dizque_instance

    def get_ffmpeg_urls_raw(self, channel_number: int) -> str:
        """
        Get raw FFMPEG URL list for channel

        :param channel_number: Number of channel to get playlist for
        :type channel_number: int
        :return: Raw text of list of FFMPEG URLs
        :rtype: str
        """
        if channel_number not in self._dizque_instance.channel_numbers:
            raise Exception(f"Channel {channel_number} does not exist.")
        url = f"{self._dizque_instance.url}/playlist?channel={channel_number}"
        response = requests.get(url=url, log='info')
        if not response:
            return ""
        return response.text

    def get_ffmpeg_urls(self, channel_number: int) -> List[str]:
        """
        Get FFMPEG URL list for channel

        :param channel_number: Number of channel to get playlist for
        :type channel_number: int
        :return: List of FFMPEG URLs
        :rtype: str
        """
        urls = self.get_ffmpeg_urls_raw(channel_number=channel_number)
        urls = urls.splitlines()
        cleaned_urls = []
        for url in urls[1:]:
            cleaned_urls.append(url.split(" ")[1].replace("'", ""))
        return cleaned_urls

    def get_ffmpeg_url(self, channel_number: int) -> str:
        """
        Get first FFMPEG URL for channel

        :param channel_number: Number of channel to get playlist for
        :type channel_number: int
        :return: FFMPEG URL
        :rtype: str
        """
        urls = self.get_ffmpeg_urls(channel_number=channel_number)
        if urls:
            return urls[0]
        return ""