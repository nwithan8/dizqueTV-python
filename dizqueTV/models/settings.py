from dizqueTV import decorators
from dizqueTV.models.base import BaseAPIObject, BaseObject


class ServerDetails(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.server_version = data.get('dizquetv')
        self.ffmpeg_version = data.get('ffmpeg')
        self.nodejs_version = data.get('nodejs')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.server_version})"

    @decorators.check_for_dizque_instance
    def reload(self):
        """
        Reload current ServerDetails object

        :return: None
        :rtype: None
        """
        temp_settings = self._dizque_instance.xmltv_settings
        if temp_settings:
            json_data = temp_settings._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_settings

class XMLTVSettings(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.cache = data.get('cache')
        self.refresh = data.get('refresh')
        self.file = data.get('file')
        self._id = data.get('_id')

    def __repr__(self):
        return f"{self.__class__.__name__}({self._id})"

    @decorators.check_for_dizque_instance
    def reload(self):
        """
        Reload current XMLTVSettings object

        :return: None
        :rtype: None
        """
        temp_settings = self._dizque_instance.xmltv_settings
        if temp_settings:
            json_data = temp_settings._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_settings

    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit these XMLTV settings
        Automatically refreshes current XMLTVSettings object

        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance.update_xmltv_settings(**kwargs):
            self.reload()
            return True
        return False

    @decorators.check_for_dizque_instance
    def reset(self) -> bool:
        """
        Reset these XMLTV settings
        Automatically refreshes current XMLTVSettings object

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance.reset_xmltv_settings():
            self.reload()
            return True
        return False


class HDHomeRunSettings(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.tunerCount = data.get('tunerCount')
        self.autoDiscovery = data.get('autoDiscovery')
        self._id = data.get('_id')

    def __repr__(self):
        return f"{self.__class__.__name__}({self._id})"

    @decorators.check_for_dizque_instance
    def refresh(self):
        """
        Reload current HDHomeRunSettings object

        :return: None
        :rtype: None
        """
        temp_settings = self._dizque_instance.hdhr_settings
        if temp_settings:
            json_data = temp_settings._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_settings

    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit these HDHomeRun settings
        Automatically refreshes current HDHomeRunSettings object

        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance.update_hdhr_settings(**kwargs):
            self.refresh()
            return True
        return False

    @decorators.check_for_dizque_instance
    def reset(self) -> bool:
        """
        Reset these HDHomeRun settings
        Automatically refreshes current HDHomeRunSettings object

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance.reset_hdhr_settings():
            self.refresh()
            return True
        return False


class FFMPEGSettings(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.configVersion = data.get('configVersion')
        self.ffmpegPath = data.get('ffmpegPath')
        self.threads = data.get('threads')
        self.concatMuxDelay = data.get('concatMuxDelay')
        self.logFfmpeg = data.get('logFfmpeg')
        self.enableFFMPEGTranscoding = data.get('enableFFMPEGTranscoding')
        self.audioVolumePercent = data.get('audioVolumePercent')
        self.videoEncoder = data.get('videoEncoder')
        self.audioEncoder = data.get('audioEncoder')
        self.targetResolution = data.get('targetResolution')
        self.videoBitrate = data.get('videoBitrate')
        self.videoBufSize = data.get('videoBufSize')
        self.audioBitrate = data.get('audioBitrate')
        self.audioBufSize = data.get('audioBufSize')
        self.audioSampleRate = data.get('audioSampleRate')
        self.audioChannels = data.get('audioChannels')
        self.errorScreen = data.get('errorScreen')
        self.errorAudio = data.get('errorAudio')
        self.normalizeVideoCodec = data.get('normalizeVideoCodec')
        self.normalizeAudioCodec = data.get('normalizeAudioCodec')
        self.normalizeResolution = data.get('normalizeResolution')
        self.normalizeAudio = data.get('normalizeAudio')
        self.maxFPS = data.get('maxFPS')
        self.scalingAlgorithm = data.get('scalingAlgorithm')
        self._id = data.get('_id')

    def __repr__(self):
        return f"{self.__class__.__name__}({self._id})"

    @decorators.check_for_dizque_instance
    def refresh(self):
        """
        Reload current FFMPEGSettings object

        :return: None
        :rtype: None
        """
        temp_settings = self._dizque_instance.ffmpeg_settings
        if temp_settings:
            json_data = temp_settings._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_settings

    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit these FFMPEG settings
        Automatically refreshes current FFMPEGSettings object

        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance.update_ffmpeg_settings(**kwargs):
            self.refresh()
            return True
        return False

    @decorators.check_for_dizque_instance
    def reset(self) -> bool:
        """
        Reset these FFMPEG settings
        Automatically refreshes current FFMPEGSettings object

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance.reset_ffmpeg_settings():
            self.refresh()
            return True
        return False


class PlexSettings(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.streamPath = data.get('streamPath')
        self.debugLogging = data.get('debugLogging')
        self.directStreamBitrate = data.get('directStreamBitrate')
        self.transcodeBitrate = data.get('transcodeBitrate')
        self.mediaBufferSize = data.get('mediaBufferSize')
        self.transcodeMediaBufferSize = data.get('transcodeMediaBufferSize')
        self.maxPlayableResolution = data.get('maxPlayableResolution')
        self.maxTranscodeResolution = data.get('maxTranscodeResolution')
        self.videoCodecs = data.get('videoCodecs')
        self.audioCodecs = data.get('audioCodecs')
        self.maxAudioChannels = data.get('maxAudioChannels')
        self.audioBoost = data.get('audioBoost')
        self.enableSubtitles = data.get('enableSubtitles')
        self.subtitleSize = data.get('subtitleSize')
        self.updatePlayStatus = data.get('updatePlayStatus')
        self.streamProtocol = data.get('streamProtocol')
        self.forceDirectPlay = data.get('forceDirectPlay')
        self.pathReplace = data.get('pathReplace')
        self.pathReplaceWith = data.get('pathReplaceWith')
        self._id = data.get('_id')

    def __repr__(self):
        return f"{self.__class__.__name__}({self._id})"

    @decorators.check_for_dizque_instance
    def refresh(self):
        """
        Reload current PlexSettings object

        :return: None
        :rtype: None
        """
        temp_settings = self._dizque_instance.plex_settings
        if temp_settings:
            json_data = temp_settings._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_settings

    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit these Plex settings
        Automatically refreshes current PlexSettings object

        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance.update_plex_settings(**kwargs):
            self.refresh()
            return True
        return False

    @decorators.check_for_dizque_instance
    def reset(self) -> bool:
        """
        Reset these Plex settings
        Automatically refreshes current PlexSettings object

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if self._dizque_instance.reset_plex_settings():
            self.refresh()
            return True
        return False
