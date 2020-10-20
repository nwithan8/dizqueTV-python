# dizqueTV-python
[![PyPi](https://img.shields.io/pypi/dm/dizquetv?color=green&label=PyPi%20downloads&logo=Pypi&logoColor=orange&style=flat-square)](https://pypi.org/project/dizqueTV/)
[![License](https://img.shields.io/pypi/l/dizqueTV?color=orange&style=flat-square)](https://github.com/nwithan8/dizqueTV-python/blob/master/LICENSE)

[![Open Issues](https://img.shields.io/github/issues-raw/nwithan8/dizqueTV-python?color=gold&style=flat-square)](https://github.com/nwithan8/dizqueTV-python/issues?q=is%3Aopen+is%3Aissue)
[![Closed Issues](https://img.shields.io/github/issues-closed-raw/nwithan8/dizqueTV-python?color=black&style=flat-square)](https://github.com/nwithan8/dizqueTV-python/issues?q=is%3Aissue+is%3Aclosed)
[![Latest Release](https://img.shields.io/github/v/release/nwithan8/dizqueTV-python?color=red&label=latest%20release&logo=github&style=flat-square)](https://github.com/nwithan8/dizqueTV-python/releases)

[![Discord](https://img.shields.io/discord/472537215457689601?color=blue&logo=discord&style=flat-square)](https://discord.gg/7jGbCJQ)
[![Twitter](https://img.shields.io/twitter/follow/nwithan8?label=%40nwithan8&logo=twitter&style=flat-square)](https://twitter.com/nwithan8)

A Python library to interact with a [dizqueTV](https://github.com/vexorian/dizquetv) instance

## Installation
#### From GitHub
1. Clone repository with ``git clone https://github.com/nwithan8/dizqueTV-python.git``
2. Enter project folder with ``cd dizqueTV-python``
3. Install requirements with ``pip install -r requirements.txt``

#### From PyPi
Run ``pip install dizqueTV``

## Setup
Import the ``API`` class from the ``dizqueTV`` module

Ex.
```
from dizqueTV import API

dtv = API(url="http://localhost:8000")
```
Enable verbose logging by passing ``verbose=True`` into the ``API`` object declaration
 
 
## Usage

### Methods
#### Channels
- Get all channels: ``channels = dtv.channels`` -> list of ``Channel`` objects
- Get all channel numbers: ``channel_numbers = dtv.channel_numbers`` -> list of ints
- Get a specific channel: ``channel = dtv.get_channel(channel_number: int)`` -> ``Channel`` object
- Get brief info on a specific channel: ``channel_info = dtv.get_channel_info(channel_number: int)`` -> ``{"name": str, "number": int, "icon": str}``
- Add a channel: ``new_channel = dtv.add_channel(programs: [Program, PlexAPI Video, ...], plex_server: PlexAPI Server [Optional], handle_errors: bool, **kwargs)`` -> ``Channel`` object
- Update a channel: ``updated = dtv.update_channel(channel_number: int, **kwargs)`` or ``Channel.update(**kwargs)`` -> True/False
- Delete a channel: ``deleted = dtv.delete_channel(channel_number: int)`` or ``Channel.delete()`` -> True/False
- Refresh a channel: ``Channel.refresh()`` -> None (reloads ``Channel`` object in-place)
- Edit channel's watermark: ``edited = Watermark.update(**kwargs)`` -> True/False
- Edit channel's FFMPEG settings: ``edited = ChannelFFMPEGSettings.update(**kwargs)`` -> True/False

#### Programs
- Get a channel's programs: ``programs = Channel.programs`` -> list of ``MediaItem`` objects
- Add program (or PlexAPI Video) to a channel: ``added = Channel.add_program(plex_item: PlexAPI Video, plex_server: PlexAPI Server, program: Program, **kwargs)`` -> True/False
- Add multiple programs (or PlexAPI Video) to a channel: ``added = Channel.add_fillers(programs: [Program, PlexAPI Video, ...], plex_server: PlexAPI Server)`` -> True/False
- Add multiple programs to multiple channels: ``added = dtv.add_programs_to_channels(programs: [Program], channels: [Channel], channel_numbers: [int])`` -> True/False
- Add X number of show episodes: ``added = Channel.add_x_number_of_show_episodes(number_of_episodes: int, list_of_episodes: [Program, Episode, ...], plex_server: PServer (Optional))`` -> True/False
- Add X duration of show episodes: ``added = Channel.add_x_duration_of_show_episodes(duration_in_milliseconds: int, list_of_episodes: [Program, Episode, ...], plex_server: PServer (Optional), allow_overtime: bool)`` -> True/False
- Delete a program: ``deleted = Channel.delete_program(program: Program)`` -> True/False
- Delete all programs: ``deleted = Channel.delete_all_programs()`` -> True/False
- Delete all episodes of a show (or of a season): ``deleted = Channel.delete_show(show_name: str, season_number: int (Optional))`` -> True/False
- Sort programs by release date: ``sorted = Channel.sort_programs_by_release_date()`` -> True/False
- Sort programs by season order: ``sorted = Channel.sort_programs_by_season_order()`` -> True/False
- Sort programs alphabetically: ``sorted = Channel.sort_programs_alphabetically()`` -> True/False
- Sort programs by duration: ``sorted = Channel.sort_programs_by_duration()`` -> True/False
- Sort programs randomly: ``sorted = Channel.sort_programs_randomly()`` -> True/False
- Sort programs cylically: ``sorted = Channel.cyclical_shuffle()`` -> True/False
- Sort programs by block shuffle: ``sorted = Channel.block_shuffle(block_length: int, randomize: bool)`` -> True/False
- Repeat programs: ``repeated = Channel.replicate(how_many_times: int)`` -> True/False
- Repeat and shuffle programs ``repeated = Channel.replicate_and_shuffle(how_many_times: int)`` -> True/False
- Remove duplicate programs: ``sorted = Channel.remove_duplicate_programs()`` -> True/False
- Remove specials: ``sorted = Channel.remove_specials()`` -> True/False
- Remove redirects: ``sorted = Channel.remove_redirects()`` -> True/False
- Balance shows: ``balanced = Channel.balance_programs(margin_of_error: float)`` -> True/False
- Add pad times: ``added = Channel.pad_times(start_every_x_minutes: int)`` -> True/False
- Add reruns: ``added = Channel.add_reruns(start_time: datetime.datetime, length_hours: int, times_to_repeat: int)`` -> True/False
- Add "Channel at Night": ``added = Channel.add_channel_at_night(night_channel_number: int, start_hour: int (24-hour time), end_hour: int (24-hour time))`` -> True/False
- Fast forward: ``success = Channel.fast_forward(seconds: int, minutes: int, hours: int, days: int, months: int, years: int)`` -> True/False
- Rewind: ``success = Channel.rewind(seconds: int, minutes: int, hours: int, days: int, months: int, years: int)`` -> True/False

#### Filler (Flex)
- Get a filler list: ``filler_list = dtv.get_filler_list(filler_list_id: str)`` -> ``FillerList`` object
- Get all filler lists: ``filler_lists = dtv.filler_lists`` -> List of ``FillerList`` objects
- Get a filler list info: ``filler_list_info = dtv.get_filler_list_info(filler_list_id: str)`` or ``FillerList.details`` -> JSON
- Get a filler list's channels: ``filler_list_channels = dtv.get_filler_list_channels(filler_list_id: str)`` or ``FillerList.channels`` -> List of ``Channel`` objects
- Get a filler list's content: ``filler_list_contents = FillerList.contents`` -> List of ``FillerItem`` objects
- Add a filler list: ``new_filler_list = dtv.add_filler_list(content: [Program, Video, Movie, Episode, ...], plex_server: PlexAPI Server, handle_errors: bool, **kwargs)`` -> ``FillerList`` object
- Update a filler list: ``updated = dtv.update_filler_list(filler_list_id: str, **kwargs)`` or ``FillerList.update(**kwargs)`` -> True/False
- Delete a filler list: ``deleted = dtv.delete_filler_list(filler_list_id: str)`` or ``FillerList.delete()`` -> True/False
- Refresh a filler list: ``FillerList.refresh()`` -> None (reloads ``FillerList`` object in-place)
- Add a filler list to a channel: ``added = Channel.add_filler_list(filler_list: FillerList, filler_list_id: str, weight: int, cooldown: int)`` -> True/False
- Add multiple filler lists to multiple channels: ``added = dtv.add_filler_lists_to_channels(filler_lists: [FillerList, ...], channels: [Channel, ...], channel_numbers: [int, ...])`` -> True/False
- Delete a filler list from a channel: ``deleted = Channel.delete_filler_list(filler_list: FillerList, filler_list_id: str)`` -> True/False
- Delete all filler lists from a channel: ``deleted = Channel.delete_all_filler_lists()`` -> True/False
- Add a filler item (or PlexAPI Video) to a filler list: ``added = FillerList.add_filler(plex_item: plexapi.media.Video/Movie/Episode, plex_server: PlexAPI Server, filler: FillerItem, **kwargs)`` -> True/False
- Add multiple filler items (or PlexAPI Video) to a filler list: ``added = FillerList.add_fillers(fillers: [FillerItem, plexapi.media.Video/Movie/Episode, ...], plex_server: PlexAPI Server)`` -> True/False
- Delete a filler item: ``deleted = FillerList.delete_filler(filler: FillerItem)`` -> True/False
- Delete all filler items: ``deleted = FillerList.delete_all_fillers()`` -> True/False
- Sort filler items by duration: ``sorted = FillerList.sort_filler_by_duration()`` -> True/False
- Sort filler items randomly: ``sorted = FillerList.sort_filler_randomly()`` -> True/False
- Remove duplicate filler items: ``sorted = FillerList.remove_duplicate_fillers()`` -> True/False

#### Scheduling
- Get a channel's schedule: ``schedule = Channel.schedule`` -> ``Schedule`` object
- Add a schedule to a channel: ``added = Channel.add_schedule(time_slots: [TimeSlot, ...], **kwargs)`` -> True/False
- Update a channel's schedule: ``updated = Channel.update_schedule(**kwargs)`` or ``Schedule.update(**kwargs)`` -> True/False
- Delete a channel's schedule: ``deleted = Channel.delete_schedule()`` or ``Schedule.delete()`` -> True/False
- Add a time slot to a schedule: ``added = Schedule.add_time_slot(time_slot: TimeSlot, time_string: str, **kwargs)`` -> True/False
- Edit a time slot on a schedule: ``edited = Schedule.edit_time_slot(time_slot: TimeSlot, time_string: str, **kwargs)`` or ``TimeSlot.edit(time_string: str, **kwargs)`` -> True/False
- Delete a time slot on a schedule: ``deleted = Schedule.delete_time_slot(time_slot: TimeSlot)`` or ``TimeSlot.delete()`` -> True/False

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
- Refresh XMLTV XML file server-side: ``refreshed = dtv.refresh_xml()`` -> True/False
- Get M3U playlist: ``m3u = dtv.channels_m3u`` -> ``m3u8`` object
- Get HLS playlist: ``hls = dtv.hls_m3u`` -> ``m3u8`` object
- Get last time XMLTV was refreshed: ``last_time = dtv.last_xmltv_refresh`` -> str

#### Guide
- Get dizqueTV guide: ``guide = dtv.guide`` -> ``Guide`` object
- Get last guide update time: ``update_time = dtv.last_guide_update`` or ``Guide.last_update`` -> ``datetime.datetime`` object
- Get guide channel numbers: ``guide_numbers = dtv.guide_channel_numbers`` -> List of strings (not ints)
- Get guide channels: ``guide_channels = Guide.channels`` -> List of ``GuideChannel`` objects
- Get guide lineup data (JSON): ``guide_lineup = dtv.guide_lineup_json`` -> JSON
- Get guide channel lineup (``GuideProgram`` objects): ``guide_lineup = GuideChannel.get_lineup(from_date: datetime.datetime, to_date: datetime.datetime)`` -> List of ``GuideProgram`` objects

#### Helper
- Convert a Python PlexAPI Video to a Program: ``program = dtv.convert_plex_item_to_program(plex_item: PlexAPI Video, plex_server: PlexAPI Server)`` or ``program = Channel.convert_plex_item_to_program(plex_item: PlexAPI Video, plex_server: PlexAPI Server)`` -> Program
- Convert a Python PlexAPI Video to a Filler: ``filler = dtv.convert_plex_item_to_filler(plex_item: PlexAPI Video, plex_server: PlexAPI Server)`` or ``filler = Channel.convert_plex_item_to_filler(plex_item: PlexAPI Video, plex_server: PlexAPI Server)`` -> Program
- Convert a Python PlexAPI Server to a PlexServer: ``server = dtv.convert_plex_server_to_dizque_plex_server(plex_server: PlexAPI Server)`` -> PlexServer
- Convert a DizqueTV Program or Redirect to a TimeSlot: ``time_slot = dtv.make_time_slot_from_dizque_program(program: Union[Program, Redirect], time: str, order: str)`` -> ``TimeSlot`` object
- Repeat a list: ``repeated_list = dtv.repeat_list(items: List, how_many_times: int)`` -> List
- Repeat and shuffle a list: ``repeated_list = dtv.repeate_and_shuffle_list(items: List, how_many_times: int)`` -> List




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
- ``programs``: list of ``Program`` objects
- ``filler_lists``: List of ``FillerList`` objects
- ``fillerRepeatCooldown``: int
- ``fallback``: List of ``FillerItem`` objects
- ``icon``: str(url)
- ``disableFillerOverlay``: bool
- ``startTime``: str(datetime)
- ``offlinePicture``: str(url)
- ``offlineSoundtrack``: str(url)
- ``offlineMode``: str
- ``number``: int
- ``name``: str
- ``duration``: int
- ``watermark``: ``Watermark`` object
- ``transcoding``: ``ChannelFFMPEGSettings`` object
- ``schedule``: ``Schedule`` object
- ``schedulableItems``: List of ``TimeSlotItem`` objects
- ``stealth``: bool
- ``json``: JSON

#### Watermark
- ``enabled``: bool
- ``width``: float
- ``verticalMargin``: float
- ``horizontalMargin``: float
- ``duration``: int
- ``fixedSize``: bool
- ``position``: str
- ``url``: str
- ``animated``: bool
- ``json``: JSON

#### Schedule
- ``lateness``: int
- ``maxDays``: int
- ``slots``: List of ``TimeSlot`` objects
- ``pad``: int
- ``timeZoneOffset``: int

#### TimeSlot
- ``time``: int
- ``showId``: str
- ``order``: str

#### TimeSlotItem
- ``showId``: str

#### Program
- ``title``: str
- ``key``: str
- ``ratingKey``: str(int)
- ``icon``: str(url)
- ``type``: str
- ``duration``: int
- ``summary``: str
- ``rating``: str
- ``date``: str
- ``year``: int
- ``plexFile``: str
- ``file``: str
- ``showTitle``: str
- ``episode``: int
- ``season``: int
- ``showIcon``: str(url)
- ``episodeIcon``: str(url)
- ``seasonIcon``: str(url)
- ``serverKey``: str
- ``isOffline``: false

#### FillerList
- ``id``: str
- ``name``: str
- ``count``: int
- ``details``: JSON
- ``content``: List of ``FillerItem`` objects
- ``channels``: List of ``Channel`` objects

#### FillerItem
- ``title``: str
- ``key``: str
- ``ratingKey``: str(int)
- ``icon``: str(url)
- ``type``: str
- ``duration``: int
- ``summary``: str
- ``date``: str
- ``year``: int
- ``plexFile``: str
- ``file``: str
- ``showTitle``: str
- ``episode``: int
- ``season``: int
- ``showIcon``: str(url)
- ``episodeIcon``: str(url)
- ``seasonIcon``: str(url)
- ``serverKey``: str
- ``isOffline``: false

#### Redirect
- ``type``: "redirect"
- ``duration``: int
- ``channel``: int
- ``isOffline``: true

#### PlexServer
- ``name``: str
- ``uri``: str(url)
- ``accessToken``: str
- ``index``: int
- ``arChannels``: bool
- ``arGuide``: bool

#### XMLTVSettings
- ``cache``: int
- ``refresh``: int
- ``file``: str

#### PlexSettings
- ``streamPath``: str
- ``debugLogging``: bool
- ``directStreamBitrate``: str(int)
- ``transcodeBitrate``: str(int)
- ``mediaBufferSize``: int
- ``transcodeMediaBufferSize``: int
- ``maxPlayableResolution``: str
- ``maxTranscodeResolution``: str
- ``videoCodecs``: str
- ``audioCodecs``: str
- ``maxAudioChannels``: str(int)
- ``audioBoost``: str(int)
- ``enableSubtitles``: bool
- ``subtitleSize``: str(int)
- ``updatePlayStatus``: bool
- ``streamProtocol``: str
- ``forceDirectPlay``: bool
- ``pathReplace``: str
- ``pathReplaceWith``: str

#### FFMPEGSettings
- ``configVersion``: int
- ``ffmpegPath``: str
- ``threads``: int
- ``concatMuxDelay``: str(int)
- ``logFfmpeg``: bool
- ``enableFFMPEGTranscoding``: bool
- ``audioVolumePercent``: int
- ``videoEncoder``: str
- ``audioEncoder``: str
- ``targetResolution``: str
- ``videoBitrate``: int
- ``videoBufSize``: int
- ``audioBitrate``: int
- ``audioBufSize``: int
- ``audioSampleRate``: int
- ``audioChannels``: int
- ``errorScreen``: str
- ``errorAudio``: str
- ``normalizeVideoCodec``: bool
- ``normalizeAudioCodec``: bool
- ``normalizeResolution``: bool
- ``normalizeAudio``: bool
- ``maxFPS``: int

#### ChannelFFMPEGSettings
- ``targetResolution``: str
- ``videoBitrate``: int
- ``videoBufSize``: int
- ``json``: JSON

#### HDHomeRunSettings
- ``tunerCount``: int
- ``autoDiscovery``: bool

### Exceptions
- ``MissingSettingsError``: The kwargs you have provided to create a new object (ex. ``Channel`` or ``PlexServer``) are incomplete
- ``MissingParametersError``: You did not provide a required parameter in your function call (ex. provide a PlexAPI Server when adding PlexAPI Video to a channel)
- ``NotRemoteObjectError``: The object you are calling this method on is a locally-created object that does not exist on the dizqueTV server
- ``ChannelCreationError``: An error occurred when creating a Channel object

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