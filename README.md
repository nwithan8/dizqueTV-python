# dizqueTV-python
A Python library to interact with a [dizqueTV](https://github.com/vexorian/dizquetv) instance

## Installation
1. Clone repository with ``git clone https://github.com/nwithan8/dizqueTV-python.git``
2. Enter project folder with ``cd dizqueTV-python``
3. Install requirements with ``pip install -r requirements``

## Setup
Import the ``API`` class from the ``dizqueTV.dizqueTV`` module

Ex.
```
from dizqueTV import dizqueTV

dtv = dizqueTV.API(url="http://localhost:8000")
```
Enable verbose logging by passing ``verbose=True`` into the ``API`` object declaration
 
 
## Usage

### Methods
#### Channels
- Get all channels: ``channels = dtv.channels`` -> list of ``Channel`` objects
- Get all channel numbers: ``channel_numbers = dtv.channel_numbers`` -> list of ints
- Get a specific channel: ``channel = dtv.get_channel(channel_number: int)`` -> ``Channel`` object
- Get brief info on a specific channel: ``channel_info = dtv.get_channel_info(channel_number: int)`` -> ``{"name": str, "number": int, "icon": str}``
- Add a channel: ``new_channel = dtv.add_channel(**kwargs)`` -> ``Channel`` object
- Update a channel: ``updated = dtv.update_channel(channel_number: int, **kwargs)`` or ``Channel.update(**kwargs)`` -> True/False
- Delete a channel: ``deleted = dtv.delete_channel(channel_number: int)`` or ``Channel.delete()`` -> True/False
- Refresh a channel: ``Channel.refresh()`` -> None (reloads ``Channel`` object in-place)
- Get a channel's programs: ``programs = Channel.programs`` -> list of ``MediaItem`` objects
- Get a channel's filler (Flex) items: ``filler = Channel.filler`` -> list of ``MediaItem`` objects

#### Plex
- Get all Plex Media Servers: ``servers = dtv.plex_servers`` -> list of ``PlexServer`` objects
- Get a specific Plex Media Server: ``server = dtv.get_plex_server(server_name: str)`` -> ``PlexServer`` object
- Get a specific Plex Media Server status: ``status = dtv.plex_server_status(server_name: str)`` or ``PlexServer.status`` -> True/False
- Get a specific Plex Media Server foreign status: ``status = dtv.plex_server_foreign_status(server_name: str)`` or ``PlexServer.foreign_status`` -> True/False
- Add a Plex Media Server: ``new_server = dtv.add_plex_server(**kwargs)`` -> ``PlexServer`` object
- Update a Plex Media Server: ``updated = dtv.update_plex_server(server_name: str, **kwargs)`` or ``PlexServer.update(**kwargs)`` -> True/False
- Delete a Plex Media Server: ``deleted = dtv.delete_plex_server(server_name: str)`` or ``PlexServer.delete()`` -> True/False
- Refresh a Plex Media Server: ``PlexServer.refresh()`` -> None (reloads ``PlexServer`` object in-place)

#### Settings
- Get FFMPEG settings: ``settings = dtv.ffmpeg_settings`` -> ``FFMPEGSettings`` object
- Update FFMPEG settings: ``updated = dtv.update_ffmpeg_settings(**kwargs)`` or ``FFMPEGSettings.update(**kwargs)`` -> True/False
- Refresh FFMPEG settings: ``FFMPEGSettings.refresh()`` -> None (reloads ``FFMPEGSettings`` object in-place)
- Reset FFMPEG settings: ``reset = dtv.reset_ffmpeg_settings()`` -> True/False
- Get Plex settings: ``settings = dtv.plex_settings`` -> ``PlexSettings`` object
- Update Plex settings: ``updated = dtv.update_plex_settings(**kwargs)`` or ``PlexSettings.update(**kwargs)`` -> True/False
- Refresh Plex settings: ``PlexSettings.refresh()`` -> None (reloads ``PlexSettings`` object in-place)
- Reset Plex settings: ``reset = dtv.reset_plex_settings()`` -> True/False
- Get XMLTV settings: ``settings = dtv.xmltv_settings`` -> ``XMLTVSettings`` object
- Update XMLTV settings: ``updated = dtv.update_xmltv_settings(**kwargs)`` or ``XMLTVSettings.update(**kwargs)`` -> True/False
- Refresh XMLTV settings: ``XMLTVSettings.reload()`` -> None (reloads ``XMLTVSettings`` object in-place)
- Reset XMLTV settings: ``reset = dtv.reset_xmltv_settings()`` -> True/False
- Get HDHomeRun settings: ``settings = dtv.hdhr_settings`` -> ``HDHomeRunSettings`` object
- Update HDHomeRun settings: ``updated = dtv.update_hdhr_settings(**kwargs)`` or ``HDHomeRunSettings.update(**kwargs)`` -> True/False
- Refresh HDHomeRun settings: ``HDHomeRunSettings.refresh()`` -> None (reloads ``HDHomeRunSettings`` object in-place)
- Reset HDHomeRun settings: ``reset = dtv.reset_hdhr_settings()`` -> True/False

#### Information
- Get dizqueTV version: ``version = dtv.dizquetv_version`` -> str
- Get FFMPEG version: ``version = dtv.ffmpeg_version`` -> str
- Get XMLTV XML file: ``xml = dtv.xmltv_xml`` -> ``xml.etree.ElementTree.Element`` object
- Get M3U playlist: ``m3u = dtv.m3u`` -> ``m3u8`` object
- Get last time XMLTV was refreshed: ``last_time = dtv.last_xmltv_refresh`` -> str





### Classes
#### API
- ``url``: dizqueTV API base url
- ``verbose``: use verbose logging (default: False)
- ``dizquetv_version``: str
- ``ffmpeg_version``: str
- ``plex_servers``: list of ``PlexServer`` objects
- ``channels``: list of ``Channel`` objects
- ``channel_numbers``: list of ints
- ``ffmpeg_settings``: ``FFMPEGSettings`` object
- ``plex_settings``: ``PlexSettings`` object
- ``xmltv_settings``: ``XMLTVSettings`` object
- ``hdhr_settings``: ``HDHomeRunSettings`` object
- ``last_xmltv_refresh``: str
- ``xmltv_xml``: ``xml.etree.ElementTree.Element`` object
- ``m3u``: ``m3u8`` object

#### Channel
- ``programs``: list of ``MediaItem`` objects
- ``filler``: list of ``MediaItem`` objects
- ``fillerRepeatCooldown``
- ``fallback``
- ``icon``
- ``disableFillerOverlay``
- ``iconWidth``
- ``iconDuration``
- ``iconPosition``
- ``overlayIcon``
- ``startTime``
- ``offlinePicture``
- ``offlineSoundtrack``
- ``offlineMode``
- ``number``
- ``name``
- ``duration``

#### MediaItem
- ``title``
- ``key``
- ``ratingKey``
- ``icon``
- ``type``
- ``duration``
- ``summary``
- ``rating``
- ``date``
- ``year``
- ``plexFile``
- ``file``
- ``showTitle``
- ``episode``
- ``season``
- ``serverKey``
- ``isOffline``

#### PlexServer
- ``name``
- ``uri``
- ``accessToken``
- ``index``
- ``arChannels``
- ``arGuide``

#### XMLTVSettings
- ``cache``
- ``refresh``
- ``file``

#### PlexSettings
- ``streamPath``
- ``debugLogging``
- ``transcodeBitrate``
- ``mediaBufferSize``
- ``transcodeMediaBufferSize``
- ``maxPlayableResolution``
- ``maxTranscodeResolution``
- ``videoCodecs``
- ``audioCodecs``
- ``maxAudioChannels``
- ``audioBoost``
- ``enableSubtitles``
- ``subtitleSize``
- ``updatePlayStatus``
- ``streamProtocol``
- ``forceDirectPlay``
- ``pathReplace``
- ``pathReplaceWith``

#### FFMPEGSettings
- ``configVersion``
- ``ffmpegPath``
- ``threads``
- ``concatMuxDelay``
- ``logFfmpeg``
- ``enableFFMPEGTranscoding``
- ``audioVolumePercent``
- ``videoEncoder``
- ``audioEncoder``
- ``targetResolution``
- ``videoBitrate``
- ``videoBufSize``
- ``audioBitrate``
- ``audioBufSize``
- ``audioSampleRate``
- ``audioChannels``
- ``errorScreen``
- ``errorAudio``
- ``normalizeVideoCodec``
- ``normalizeAudioCodec``
- ``normalizeResolution``
- ``normalizeAudio``

#### HDHomeRunSettings
- ``tunerCount``
- ``autoDiscovery``

## Contact
Please leave a pull request if you would like to contribute.

Join the dizqueTV Discord server (link on [project page](https://github.com/vexorian/dizquetv)). My Discord username is **nwithan8#8438**

Follow me on Twitter: [@nwithan8](https://twitter.com/nwithan8)

Also feel free to check out my other projects here on [GitHub](https://github.com/nwithan8) or join the #developer channel in my Discord server below.

<div align="center">
	<p>
		<a href="https://discord.gg/ygRDVE9"><img src="https://discordapp.com/api/guilds/472537215457689601/widget.png?style=banner2" alt="" /></a>
	</p>
</div>