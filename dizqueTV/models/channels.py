from datetime import datetime, timedelta
from typing import List, Union

from plexapi.audio import Track
from plexapi.server import PlexServer as PServer
from plexapi.video import Video, Movie, Episode

import dizqueTV.helpers as helpers
from dizqueTV import decorators
from dizqueTV.exceptions import MissingParametersError, GeneralException
from dizqueTV.models.base import BaseAPIObject, BaseObject
from dizqueTV.models.custom_show import CustomShow, CustomShowItem
from dizqueTV.models.fillers import FillerList
from dizqueTV.models.media import Redirect, Program, FillerItem
from dizqueTV.models.templates import MOVIE_PROGRAM_TEMPLATE, EPISODE_PROGRAM_TEMPLATE, TRACK_PROGRAM_TEMPLATE, \
    REDIRECT_PROGRAM_TEMPLATE, FILLER_LIST_CHANNEL_TEMPLATE, \
    CHANNEL_FFMPEG_SETTINGS_DEFAULT, SCHEDULE_SETTINGS_DEFAULT, TIME_SLOT_SETTINGS_TEMPLATE, SCHEDULE_SETTINGS_TEMPLATE, \
    RANDOM_SCHEDULE_SETTINGS_TEMPLATE, RANDOM_SCHEDULE_SETTINGS_DEFAULT


class ChannelFFMPEGSettings(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance, channel_instance):
        super().__init__(data, dizque_instance)
        self._channel_instance = channel_instance
        self.targetResolution = data.get('targetResolution')
        self.videoBitrate = data.get('videoBitrate')
        self.videoBufSize = data.get('videoBufSize')

    def __repr__(self):
        return f"{self.__class__.__name__}({(self.targetResolution if self.targetResolution else 'Default')})"

    @decorators.check_for_dizque_instance
    def update(self,
               use_global_settings: bool = False,
               **kwargs) -> bool:
        """
        Edit this channel's FFMPEG settings on dizqueTV
        Automatically refreshes associated Channel object

        :param use_global_settings: Use global dizqueTV FFMPEG settings (default: False)
        :type use_global_settings: bool, optional
        :param kwargs: keyword arguments of Channel FFMPEG settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place, ChannelFFMPEGSettings object is destroyed)
        :rtype: bool
        """
        if use_global_settings:
            new_settings = CHANNEL_FFMPEG_SETTINGS_DEFAULT
        else:
            new_settings = helpers._combine_settings(new_settings_dict=kwargs,
                                                     default_dict=self._data)
        if self._dizque_instance.update_channel(channel_number=self._channel_instance.number,
                                                transcoding=new_settings):
            self._channel_instance.refresh()
            del self
            return True
        return False


class ChannelOnDemandSettings(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance, channel_instance):
        super().__init__(data, dizque_instance)
        self._channel_instance = channel_instance
        self.isOnDemand = data.get('isOnDemand')
        self.modulo = data.get('modulo')
        self.paused = data.get('paused')
        self.firstProgramModulo = data.get('firstProgramModulo')
        self.playedOffset = data.get('playedOffset')

    def __repr__(self):
        return f"{self.__class__.__name__}({('On Demand' if self.isOnDemand else 'Not On Demand')})"

    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit this channel's OnDemand settings on dizqueTV
        Automatically refreshes associated Channel object


        :param kwargs: keyword arguments of Channel FFMPEG settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place, ChannelFFMPEGSettings object is destroyed)
        :rtype: bool
        """
        new_settings = helpers._combine_settings(new_settings_dict=kwargs, default_dict=self._data)
        new_settings['firstProgramModulo'] = (self._channel_instance.startTime_datetime.timestamp() * 1000) % new_settings['modulo']
        if self._dizque_instance.update_channel(channel_number=self._channel_instance.number,
                                                onDemand=new_settings):
            self._channel_instance.refresh()
            del self
            return True
        return False


class Watermark(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance, channel_instance):
        super().__init__(data, dizque_instance)
        self._channel_instance = channel_instance
        self.enabled = data.get('enabled')
        self.width = data.get('width')
        self.verticalMargin = data.get('verticalMargin')
        self.horizontalMargin = data.get('horizontalMargin')
        self.duration = data.get('duration')
        self.fixedSize = data.get('fixedSize')
        self.position = data.get('position')
        self.url = data.get('url')
        self.animated = data.get('animated')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.enabled}:{(self.url if self.url else 'Empty URL')})"

    @decorators.check_for_dizque_instance
    def update(self,
               **kwargs) -> bool:
        """
        Edit this Watermark on dizqueTV
        Automatically refreshes associated Channel object

        :param kwargs: keyword arguments of Watermark settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place, Watermark object is destroyed)
        :rtype: bool
        """
        new_watermark_dict = self._dizque_instance._fill_in_watermark_settings(**kwargs)
        if self._dizque_instance.update_channel(channel_number=self._channel_instance.number,
                                                watermark=new_watermark_dict):
            self._channel_instance.refresh()
            del self
            return True
        return False


class TimeSlotItem:
    def __init__(self,
                 item_type: str,
                 item_value: str = ""):
        self.showId = f"{item_type}.{item_value}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.showId})"


class TimeSlot(BaseObject):
    def __init__(self, data: dict, program: TimeSlotItem = None, schedule_instance=None):
        super().__init__(data)
        self.time = data.get('time')
        self.showId = (program.showId if program else data.get('showId'))
        self.order = data.get('order')
        self._schedule_instance = schedule_instance

    def __repr__(self):
        return f"{self.__class__.__name__}({self.time}:{self.showId}:{self.order})"

    def edit(self, time_string: str = None, **kwargs) -> bool:
        """
        Edit this TimeSlot object

        :param time_string: time in readable 24-hour format (ex. 00:00:00 = 12:00:00 A.M., 05:15:00 = 5:15 A.M., 20:08:12 = 8:08:12 P.M.) (Optional if time=<milliseconds_since_midnight> not included in kwargs)
        :type time_string: str, optional
        :param kwargs: Keyword arguments for the edited time slot (time, showId and order)
        :return: True if successful, False if unsuccessful (Channel reloads in-place, this TimeSlot and its parent Schedule object are destroyed)
        :rtype: bool
        """
        if not self._schedule_instance:
            return False
        return self._schedule_instance.edit_time_slot(time_slot=self, time_string=time_string, **kwargs)

    def delete(self) -> bool:
        """
        Delete this TimeSlot object from the schedule

        :return: True if successful, False if unsuccessful (Channel reloads in-place, this TimeSlot and its parent Schedule object are destroyed)
        :rtype: bool
        """
        if not self._schedule_instance:
            return False
        return self._schedule_instance.delete_time_slot(time_slot=self)


class Schedule(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance, channel_instance):
        super().__init__(data, dizque_instance)
        self._channel_instance = channel_instance
        self.lateness = data.get('lateness')
        self.maxDays = data.get('maxDays')
        self.slots = [TimeSlot(data=slot, schedule_instance=self) for slot in data.get('slots', [])]
        self.pad = data.get('pad')
        self.timeZoneOffset = data.get('timeZoneOffset')
        self.padStyle = data.get('padStyle')
        self.randomDistribution = data.get('randomDistribution')
        self.flexPreference = data.get('flexPreference')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.maxDays} Days:{len(self.slots)} TimeSlots>"

    @decorators.check_for_dizque_instance
    def update(self,
               **kwargs):
        """
        Edit this Schedule on dizqueTV
        Automatically refreshes associated Channel object

        :param kwargs: keyword arguments of Schedule settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place, this Schedule object is destroyed)
        :rtype: bool
        """
        new_settings = helpers._combine_settings_add_new(new_settings_dict=kwargs,
                                                         default_dict=(self._data
                                                                        if self._data else SCHEDULE_SETTINGS_DEFAULT)
                                                         )
        return self._channel_instance.update_schedule(**new_settings)

    def add_time_slot(self,
                      time_slot: TimeSlot = None,
                      time_string: str = None,
                      **kwargs) -> bool:
        """
        Add a time slot to this Schedule

        :param time_slot: TimeSlot object to add (Optional)
        :type time_slot: TimeSlot, optional
        :param time_string: time in readable 24-hour format (ex. 00:00:00 = 12:00:00 A.M., 05:15:00 = 5:15 A.M., 20:08:12 = 8:08:12 P.M.) (Optional if time=<milliseconds_since_midnight> not included in kwargs)
        :type time_string: str, optional
        :param kwargs: keyword arguments for a new time slot (time, showId and order)
        :return: True if successful, False if unsuccessful (Channel reloads in-place, this Schedule object is destroyed)
        :rtype: bool
        """
        if time_slot:
            kwargs = time_slot._data
        else:
            if time_string:
                kwargs['time'] = helpers.convert_24_time_to_milliseconds_past_midnight(time_string=time_string)
            new_settings_filtered = helpers._filter_dictionary(new_dictionary=kwargs,
                                                               template_dict=TIME_SLOT_SETTINGS_TEMPLATE)
            if not helpers._settings_are_complete(new_settings_dict=new_settings_filtered,
                                                  template_settings_dict=TIME_SLOT_SETTINGS_TEMPLATE):
                raise GeneralException("Missing settings required to make a time slot.")

            kwargs = new_settings_filtered
        if kwargs['showId'] not in [item.showId for item in self._channel_instance.scheduledableItems]:
            raise GeneralException(f"Program {kwargs['showId']} cannot be added to a time slot. "
                                   f"Please make sure the program is added to the channel first.")
        slots = self._data.get('slots', [])
        if kwargs['time'] in [slot['time'] for slot in slots]:
            raise GeneralException(f"Time slot {kwargs['time']} is already filled.")
        slots.append(kwargs)
        return self.update(slots=slots)

    def edit_time_slot(self, time_slot: TimeSlot, time_string: str = None, **kwargs) -> bool:
        """
        Edit a time slot from this Schedule

        :param time_slot: TimeSlot object to edit
        :type time_slot: TimeSlot
        :param time_string: time in readable 24-hour format (ex. 00:00:00 = 12:00:00 A.M., 05:15:00 = 5:15 A.M., 20:08:12 = 8:08:12 P.M.) (Optional if time=<milliseconds_since_midnight> not included in kwargs)
        :type time_string: str optional
        :param kwargs: Keyword arguments for the edited time slot (time, showId and order)
        :return: True if successful, False if unsuccessful (Channel reloads in-place, this Schedule object is destroyed)
        :rtype: bool
        """
        if time_string:
            kwargs['time'] = helpers.convert_24_time_to_milliseconds_past_midnight(time_string=time_string)
        current_slots = self._data.get('slots', [])
        new_slots = []
        for slot in current_slots:
            if slot['time'] != time_slot.time:
                new_slots.append(slot)
            else:
                new_slot_data = helpers._combine_settings(new_settings_dict=kwargs, default_dict=slot)
                new_slots.append(new_slot_data)
        return self.update(slots=new_slots)

    @decorators.check_for_dizque_instance
    def delete_time_slot(self, time_slot: TimeSlot) -> bool:
        """
        Delete a time slot from this Schedule

        :param time_slot: TimeSlot object to remove
        :type time_slot: TimeSlot
        :return: True if successful, False if unsuccessful (Channel reloads in-place, this Schedule object is destroyed)
        :rtype: bool
        """
        slots = self._data.get('slots', [])
        try:
            slots.remove(time_slot._data)
            return self.update(slots=slots)
        except ValueError:
            pass
        return False

    @decorators.check_for_dizque_instance
    def delete(self) -> bool:
        """
        Delete this channel's Schedule
        Removes all duplicate programs, adds random shuffle

        :return: True if successful, False if unsuccessful (Channel reloads in-place, this Schedule object is destroyed)
        :rtype: bool
        """
        return self._channel_instance.delete_schedule()


class Channel(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance, plex_server: PServer = None):
        super().__init__(data, dizque_instance)
        self._program_data = data.get('programs')
        self._fillerCollections_data = data.get('fillerCollections')
        self.fillerRepeatCooldown = data.get('fillerRepeatCooldown')
        self.startTime = data.get('startTime')
        self.offlinePicture = data.get('offlinePicture')
        self.offlineSoundtrack = data.get('offlineSoundtrack')
        self.offlineMode = data.get('offlineMode')
        self.number = data.get('number')
        self.name = data.get('name')
        self.duration = data.get('duration')
        self.stealth = data.get('stealth')
        self._id = data.get('_id')
        self.fallback = [FillerItem(data=filler_data,
                                    dizque_instance=dizque_instance, filler_list_instance=None)
                         for filler_data in data.get('fallback')]
        self.watermark = Watermark(data=data.get('watermark'),
                                   dizque_instance=dizque_instance,
                                   channel_instance=self) if data.get('watermark') else None
        self.transcoding = ChannelFFMPEGSettings(data=data.get('transcoding'),
                                                 dizque_instance=dizque_instance,
                                                 channel_instance=self) if data.get('transcoding') else None
        self.onDemand = ChannelOnDemandSettings(data=data.get('onDemand'),
                                                dizque_instance=dizque_instance,
                                                channel_instance=self) if data.get('onDemand') else None
        self.schedule = None
        if data.get('scheduleBackup'):
            self.schedule = Schedule(data=data.get('scheduleBackup'),
                                     dizque_instance=dizque_instance,
                                     channel_instance=self)
        self.plex_server = plex_server
        self.scheduledableItems = self._get_schedulable_items()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.number}:{self.name})"

    @property
    def startTime_datetime(self) -> datetime:
        return helpers.string_to_datetime(date_string=self.startTime)

    def _get_schedulable_items(self) -> List[TimeSlotItem]:
        """
        Get all programs able to be scheduled for this channel

        :return: List of TimeSlotItem objects
        :rtype: List[TimeSlotItem]
        """
        used_titles = []
        schedulable_items = []
        for program in self.programs:
            if program.type == 'customShow':  # custom shows not schedulable at this time
                pass
            elif program.type == 'redirect' and program.channel not in used_titles:
                schedulable_items.append(TimeSlotItem(item_type='redirect', item_value=program.channel))
                used_titles.append(program.channel)
            elif program.showTitle and program.showTitle not in used_titles:
                if program.type == 'movie':
                    schedulable_items.append(TimeSlotItem(item_type='movie', item_value=program.showTitle))
                else:
                    schedulable_items.append(TimeSlotItem(item_type='tv', item_value=program.showTitle))
                used_titles.append(program.showTitle)
        return schedulable_items

    # CRUD Operations
    # Create (handled in dizqueTV.py)
    # Read
    @property
    def programs(self) -> List[Union[Program, CustomShow]]:
        """
        Get all programs on this channel

        :return: List of Program and CustomShow objects
        :rtype: List[Union[Program, CustomShow]]
        """
        return self._dizque_instance.parse_custom_shows_and_non_custom_shows(items=self._program_data,
                                                                             non_custom_show_type=Program,
                                                                             dizque_instance=self._dizque_instance,
                                                                             channel_instance=self)

    @decorators.check_for_dizque_instance
    def get_program(self,
                    program_title: str = None,
                    redirect_channel_number: int = None) -> Union[Program, None]:
        """
        Get a specific program on this channel

        :param program_title: Title of program
        :type program_title: str, optional
        :param redirect_channel_number: Channel number for Redirect object (use if getting Redirect instead of Program)
        :type redirect_channel_number: int, optional
        :return: Program object or None
        :rtype: Program
        """
        if not program_title and not redirect_channel_number:
            raise MissingParametersError("Please include either a program_title or a redirect_channel_number.")
        for program in self.programs:
            if (program_title and program.title == program_title) \
                    or (redirect_channel_number and redirect_channel_number == program.channel):
                return program
        return None

    @property
    def filler_lists(self) -> List[FillerList]:
        """
        Get all filler lists on this channel

        :return: List of FillerList objects
        :rtype: List[FillerList]
        """
        return [FillerList(data=filler_list, dizque_instance=self._dizque_instance)
                for filler_list in self._fillerCollections_data]

    @decorators.check_for_dizque_instance
    def get_filler_list(self,
                        filler_list_title: str) -> Union[FillerList, None]:
        """
        Get a specific filler list on this channel

        :param filler_list_title: Title of filler list
        :type filler_list_title: str
        :return: FillerList object or None
        :rtype: FillerList
        """
        for filler_list in self.filler_lists:
            if filler_list.name == filler_list_title:
                return filler_list
        return None

    # Update
    @decorators.check_for_dizque_instance
    def refresh(self):
        """
        Reload current Channel object
        Use to update program and filler data

        :return: None
        """
        temp_channel = self._dizque_instance.get_channel(channel_number=self.number)
        if temp_channel:
            json_data = temp_channel._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_channel

    @decorators.check_for_dizque_instance
    def update(self,
               **kwargs) -> bool:
        """
        Edit this Channel on dizqueTV
        Automatically refreshes current Channel object

        :param kwargs: keyword arguments of Channel settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        if self._dizque_instance.update_channel(channel_number=self.number, **kwargs):
            self.refresh()
            return True
        return False

    @decorators.check_for_dizque_instance
    def edit(self,
             **kwargs) -> bool:
        """
        Alias for channels.update()

        :param kwargs: keyword arguments of Channel settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        return self.update(**kwargs)

    @decorators.check_for_dizque_instance
    def add_program(self,
                    plex_item: Union[Video, Movie, Episode, Track] = None,
                    plex_server: PServer = None,
                    program: Union[Program, CustomShow] = None,
                    **kwargs) -> bool:
        """
        Add a program to this channel

        :param plex_item: plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode or plexapi.audio.Track object (optional)
        :type plex_item: Union[plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode, plexapi.audio.Track], optional
        :param plex_server: plexapi.server.PlexServer object (optional)
        :type plex_server: plexapi.server.PlexServer, optional
        :param program: Program object (optional)
        :type program: Program, optional
        :param kwargs: keyword arguments of Program settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in place)
        :rtype: bool
        """
        if not plex_item and not program and not kwargs:
            raise MissingParametersError("Please include either a program, a plex_item/plex_server combo, or kwargs")
        if plex_item and (plex_server or self.plex_server):
            temp_program = self._dizque_instance.convert_plex_item_to_program(plex_item=plex_item,
                                                                              plex_server=(
                                                                                  plex_server if plex_server
                                                                                  else self.plex_server)
                                                                              )
            kwargs = temp_program._data
        elif program:
            if type(program) == CustomShow:
                # pass CustomShow handling to add_programs, since multiple programs need to be added
                return self.add_programs(programs=[program], plex_server=plex_server)
            else:
                kwargs = program._data
        template = MOVIE_PROGRAM_TEMPLATE
        if kwargs['type'] == 'episode':
            template = EPISODE_PROGRAM_TEMPLATE
        elif kwargs['type'] == 'track':
            template = TRACK_PROGRAM_TEMPLATE
        elif kwargs['type'] == 'redirect':
            template = REDIRECT_PROGRAM_TEMPLATE
        if helpers._settings_are_complete(new_settings_dict=kwargs,
                                          template_settings_dict=template,
                                          ignore_keys=['_id', 'id']):
            channel_data = self._data
            if not channel_data['duration']:
                channel_data['duration'] = 0
            channel_data['programs'].append(kwargs)
            channel_data['duration'] += kwargs.get('duration', 0)
            return self.update(**channel_data)
        return False

    @decorators.check_for_dizque_instance
    def add_programs(self,
                     programs: List[Union[Program, CustomShow, Video, Movie, Episode, Track]],
                     plex_server: PServer = None) -> bool:
        """
        Add multiple programs to this channel

        :param programs: List of Program, CustomShow plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode or plexapi.audio.Track objects
        :type programs: List[Union[Program, CustomShow, plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode, plexapi.audio.Track]]
        :param plex_server: plexapi.server.PlexServer object (required if adding PlexAPI Video, Movie, Episode or Track objects)
        :type plex_server: plexapi.server.PlexServer, optional
        :return: True if successful, False if unsuccessful (Channel reloads in place)
        :rtype: bool
        """
        channel_data = self._data
        if not programs:
            raise GeneralException("You must provide at least one program to add to the channel.")

        programs = self._dizque_instance.expand_custom_show_items(programs=programs)

        for program in programs:
            if type(program) not in [Program, Redirect, CustomShowItem]:
                if not plex_server and not self.plex_server:
                    raise MissingParametersError("Please include a plex_server if you are adding PlexAPI Video, "
                                                 "Movie, Episode or Track items.")
                program = self._dizque_instance.convert_plex_item_to_program(plex_item=program,
                                                                             plex_server=(
                                                                                 plex_server if plex_server
                                                                                 else self.plex_server)
                                                                             )
            channel_data['programs'].append(program._data)
            channel_data['duration'] += program.duration
        return self.update(**channel_data)

    @decorators.check_for_dizque_instance
    def update_program(self,
                       program: Program,
                       **kwargs) -> bool:
        """
        Update a program from this channel

        :param program: Program object to update
        :type program: Program
        :param kwargs: Keyword arguments of new Program settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        channel_data = self._data
        for a_program in channel_data['programs']:
            if (program.type == 'redirect' and a_program['type'] == 'redirect') \
                    or (a_program['title'] == program.title):
                if kwargs.get('duration'):
                    channel_data['duration'] -= a_program['duration']
                    channel_data['duration'] += kwargs['duration']
                new_data = helpers._combine_settings(new_settings_dict=kwargs, default_dict=a_program)
                a_program.update(new_data)
                return self.update(**channel_data)
        return False

    @decorators.check_for_dizque_instance
    def delete_program(self,
                       program: Program) -> bool:
        """
        Delete a program from this channel

        :param program: Program object to delete
        :type program: Program
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        channel_data = self._data
        for a_program in channel_data['programs']:
            if (program.type == 'redirect' and a_program['type'] == 'redirect') \
                    or (a_program['title'] == program.title):
                channel_data['duration'] -= a_program['duration']
                channel_data['programs'].remove(a_program)
                return self.update(**channel_data)
        return False

    @decorators.check_for_dizque_instance
    def delete_show(self,
                    show_name: str,
                    season_number: int = None) -> bool:
        """
        Delete all episodes of a specific show

        :param show_name: Name of show to delete
        :type show_name: str
        :param season_number: (Optional) Number of season to delete
        :type season_number: int, optional
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        all_programs = self.programs
        programs_to_add = []
        for program in all_programs:
            # collect everything that's not an episode
            if program.type != 'episode':
                programs_to_add.append(program)
            else:
                # collect everything that's not the targeted show
                if program.showTitle != show_name:
                    programs_to_add.append(program)
                else:
                    if season_number:
                        # collect everything that's not the targeted season if there is one
                        if season_number != season_number:
                            programs_to_add.append(program)
        if self.delete_all_programs():
            # add back everything that's not the targeted show/season combo
            return self.add_programs(programs=programs_to_add)
        return False

    @decorators.check_for_dizque_instance
    def add_x_number_of_show_episodes(self,
                                      number_of_episodes: int,
                                      list_of_episodes: List[Union[Program, Episode]],
                                      plex_server: PServer = None) -> bool:
        """
        Add the first X number of items from a list of programs to a dizqueTV channel

        :param number_of_episodes: number of items to add from the list
        :type number_of_episodes: int
        :param list_of_episodes: list of Program or plexapi.media.Episode objects
        :type list_of_episodes: List[Union[Program, plexapi.video.Episode]]
        :param plex_server: plexapi.server.PlexServer, needed if adding plexapi.media.Episode objects
        :type plex_server: plexapi.server.PlexServer, optional
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        channel_data = self._data
        for i in range(0, number_of_episodes):
            if not type(list_of_episodes[i]) == Program:
                if not plex_server and not self.plex_server:
                    raise MissingParametersError("Please include a plex_server if you are adding PlexAPI Video "
                                                 "or Episode items.")
                list_of_episodes[i] = self._dizque_instance.convert_plex_item_to_program(plex_item=list_of_episodes[i],
                                                                                         plex_server=(
                                                                                             plex_server if plex_server
                                                                                             else self.plex_server)
                                                                                         )
            channel_data['programs'].append(list_of_episodes[i]._data)
            channel_data['duration'] += list_of_episodes[i].duration
        return self.update(**channel_data)

    @decorators.check_for_dizque_instance
    def add_x_duration_of_show_episodes(self,
                                        duration_in_milliseconds: int,
                                        list_of_episodes: List[Union[Program, Episode]],
                                        plex_server: PServer = None,
                                        allow_overtime: bool = False) -> bool:
        """
        Add an X duration of items from a list of programs to a dizqueTV channel

        :param duration_in_milliseconds: length of time to add
        :type duration_in_milliseconds: int
        :param list_of_episodes: list of Program or plexapi.media.Episode objects
        :type list_of_episodes: List[Union[Program, plexapi.video.Episode]]
        :param plex_server: plexapi.server.PlexServer, needed if adding plexapi.media.Episode objects
        :type plex_server: plexapi.server.PlexServer, optional
        :param allow_overtime: Allow adding one more episode, even if total time would go over. Otherwise, don't add any more if total time would exceed duration_in_milliseconds (default: False)
        :type allow_overtime: bool, optional
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        channel_data = self._data
        total_runtime = 0
        list_index = 0
        while total_runtime < duration_in_milliseconds:
            if not type(list_of_episodes[list_index]) == Program:
                if not plex_server and not self.plex_server:
                    raise MissingParametersError("Please include a plex_server if you are adding PlexAPI Video "
                                                 "or Episode items.")
                list_of_episodes[list_index] = \
                    self._dizque_instance.convert_plex_item_to_program(plex_item=list_of_episodes[list_index],
                                                                       plex_server=(
                                                                           plex_server if plex_server
                                                                           else self.plex_server)
                                                                       )
            if (total_runtime + list_of_episodes[list_index].duration) > duration_in_milliseconds:
                if allow_overtime:
                    channel_data['programs'].append(list_of_episodes[list_index]._data)
                    channel_data['duration'] += list_of_episodes[list_index].duration
                else:
                    pass
            else:
                channel_data['programs'].append(list_of_episodes[list_index]._data)
                channel_data['duration'] += list_of_episodes[list_index].duration
            total_runtime += list_of_episodes[list_index].duration
            list_index += 1
        return self.update(**channel_data)

    @decorators.check_for_dizque_instance
    def delete_all_programs(self) -> bool:
        """
        Delete all programs from this channel

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        channel_data = self._data
        channel_data['duration'] -= sum(program.duration for program in self.programs)
        channel_data['programs'] = []
        return self.update(**channel_data)

    @decorators.check_for_dizque_instance
    def _delete_all_offline_times(self) -> bool:
        """
        Delete all offline program in a channel

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        programs_to_add = []
        for program in self.programs:
            if not program.isOffline or program.type == 'redirect':
                programs_to_add.append(program)
        if programs_to_add and self.delete_all_programs():
            return self.add_programs(programs=programs_to_add)
        return False

    @decorators.check_for_dizque_instance
    def add_filler_list(self,
                        filler_list: FillerList = None,
                        filler_list_id: str = None,
                        weight: int = 300,
                        cooldown: int = 0) -> bool:
        """
        Add a filler list to this channel

        :param filler_list: FillerList object (optional)
        :type filler_list: FillerList, optional
        :param filler_list_id: ID of FillerList (optional)
        :type filler_list_id: str, optional
        :param weight: weight to assign list in channel (default: 300)
        :type weight: int, optional
        :param cooldown: cooldown to assign list in channel (default: 0)
        :type cooldown: int, optional
        :return: True if successful, False if unsuccessful (Channel reloads in place)
        :rtype: bool
        """
        if not filler_list and not filler_list_id:
            raise MissingParametersError("Please include either a FillerList object or kwargs")
        if filler_list:
            filler_list_id = filler_list.id
        new_settings_dict = {
            'id': filler_list_id,
            'weight': weight,
            'cooldown': cooldown
        }
        if helpers._settings_are_complete(new_settings_dict=new_settings_dict,
                                          template_settings_dict=FILLER_LIST_CHANNEL_TEMPLATE,
                                          ignore_keys=['_id', 'id']):
            channel_data = self._data
            channel_data['fillerCollections'].append(new_settings_dict)
            # filler_list_data['duration'] += kwargs['duration']
            return self.update(**channel_data)
        return False

    @decorators.check_for_dizque_instance
    def delete_filler_list(self,
                           filler_list: FillerList = None,
                           filler_list_id: str = None) -> bool:
        """
        Delete a program from this channel

        :param filler_list: FillerList object to delete
        :type filler_list: FillerList, optional
        :param filler_list_id: ID of filler list to delete
        :type filler_list_id: str, optional
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        if not filler_list and not filler_list_id:
            raise GeneralException("You must include either a filler_list or a filler_list_id.")
        if filler_list:
            filler_list_id = filler_list.id
        channel_data = self._data
        for a_list in channel_data['fillerCollections']:
            if filler_list_id == a_list.get('id'):
                channel_data['fillerCollections'].remove(a_list)
                return self.update(**channel_data)
        return False

    @decorators.check_for_dizque_instance
    def delete_all_filler_lists(self) -> bool:
        """
        Delete all filler lists from this channel

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        channel_data = self._data
        channel_data['fillerCollections'] = []
        return self.update(**channel_data)

    # Schedule
    @decorators.check_for_dizque_instance
    def add_schedule(self, time_slots: List[TimeSlot], **kwargs) -> bool:
        """
        Add a schedule to this channel

        :param time_slots: List of TimeSlot objects
        :type time_slots: List[TimeSlot]
        :param kwargs: keyword arguments for schedule settings
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        for slot in time_slots:
            kwargs['slots'].append(slot._data)
        schedule_settings = helpers._combine_settings_enforce_types(new_settings_dict=kwargs,
                                                                    default_dict=SCHEDULE_SETTINGS_DEFAULT,
                                                                    template_dict=SCHEDULE_SETTINGS_TEMPLATE)
        if helpers._settings_are_complete(new_settings_dict=schedule_settings,
                                          template_settings_dict=SCHEDULE_SETTINGS_TEMPLATE):
            schedule = Schedule(data=schedule_settings, dizque_instance=None, channel_instance=self)
            return self._dizque_instance._make_schedule(channel=self, schedule=schedule)
        return False

    @decorators.check_for_dizque_instance
    def add_random_schedule(self, time_slots: List[TimeSlot], **kwargs) -> bool:
        """
        Add a random schedule to this channel

        :param time_slots: List of TimeSlot objects
        :type time_slots: List[TimeSlot]
        :param kwargs: keyword arguments for schedule settings
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        for slot in time_slots:
            kwargs['slots'].append(slot._data)
        schedule_settings = helpers._combine_settings_enforce_types(new_settings_dict=kwargs,
                                                                    default_dict=RANDOM_SCHEDULE_SETTINGS_DEFAULT,
                                                                    template_dict=RANDOM_SCHEDULE_SETTINGS_TEMPLATE)
        if helpers._settings_are_complete(new_settings_dict=schedule_settings,
                                          template_settings_dict=RANDOM_SCHEDULE_SETTINGS_TEMPLATE):
            schedule = Schedule(data=schedule_settings, dizque_instance=None, channel_instance=self)
            return self._dizque_instance._make_random_schedule(channel=self, schedule=schedule)
        return False

    @decorators.check_for_dizque_instance
    def update_schedule(self, **kwargs) -> bool:
        """
        Update the schedule for this channel

        :param kwargs: keyword arguments for schedule settings (slots data included if needed) (include random=true to use random time slots)
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        if kwargs.get('random', False):
            return self.add_random_schedule(time_slots=[], **kwargs)
        return self.add_schedule(time_slots=[], **kwargs)

    @decorators.check_for_dizque_instance
    def delete_schedule(self) -> bool:
        """
        Delete this channel's Schedule
        Removes all offline times, removes duplicate programs (and all redirects), random shuffles remaining items

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        self._delete_all_offline_times()
        if self.remove_duplicate_programs():  # also removes all redirects
            self.sort_programs_randomly()
        return self.update(scheduleBackup={})

    # Sort Programs
    @decorators.check_for_dizque_instance
    def sort_programs_by_release_date(self) -> bool:
        """
        Sort all programs on this channel by release date

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.sort_media_by_release_date(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def sort_programs_by_season_order(self) -> bool:
        """
        Sort all programs on this channel by season order
        Movies are added at the end of the list

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.sort_media_by_season_order(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def sort_programs_alphabetically(self) -> bool:
        """
        Sort all programs on this channel in alphabetical order

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.sort_media_alphabetically(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def sort_programs_by_duration(self) -> bool:
        """
        Sort all programs on this channel by duration

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.sort_media_by_duration(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def sort_programs_randomly(self) -> bool:
        """
        Sort all programs on this channel randomly

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.sort_media_randomly(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def cyclical_shuffle(self) -> bool:
        """
        Sort TV shows on this channel cyclically

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.sort_media_cyclical_shuffle(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def block_shuffle(self,
                      block_length: int,
                      randomize: bool = False) -> bool:
        """
        Sort TV shows on this channel cyclically

        :param block_length: Length of each block
        :type block_length: int
        :param randomize: Random block lengths between 1 and block_length
        :type randomize: bool, optional
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.sort_media_block_shuffle(media_items=self.programs,
                                                           block_length=block_length,
                                                           randomize=randomize)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def replicate(self,
                  how_many_times: int) -> bool:
        """
        Replicate/repeat the channel lineup x number of times
        Items will remain in the same order.
        Ex. [A, B, C] x3 -> [A, B, C, A, B, C, A, B, C]

        :param how_many_times: how many times to repeat the lineup
        :type how_many_times: int
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        programs = self.programs
        final_program_list = []
        for _ in range(0, how_many_times):
            for program in programs:
                final_program_list.append(program)
        if final_program_list and self.delete_all_programs():
            return self.add_programs(programs=final_program_list)
        return False

    @decorators.check_for_dizque_instance
    def replicate_and_shuffle(self,
                              how_many_times: int) -> bool:
        """
        Replicate/repeat the channel lineup, shuffled, x number of times
        Items will be shuffled in each repeat group.
        Ex. [A, B, C] x3 -> [A, B, C, B, A, C, C, A, B]

        :param int how_many_times: how many times to repeat the lineup
        :type how_many_times: int
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        programs = self.programs
        final_program_list = []
        for _ in range(0, how_many_times):
            list_to_shuffle = programs
            helpers.shuffle(list_to_shuffle)
            for program in list_to_shuffle:
                final_program_list.append(program)
        if final_program_list and self.delete_all_programs():
            return self.add_programs(programs=final_program_list)
        return False

    @decorators.check_for_dizque_instance
    def remove_duplicate_programs(self) -> bool:
        """
        Delete duplicate programs on this channel
        NOTE: Removes all redirects

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.remove_duplicate_media_items(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def remove_duplicate_redirects(self) -> bool:
        """
        Delete duplicate redirects on this channel

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.remove_duplicates_by_attribute(items=self.programs, attribute_name='channel')
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def remove_redirects(self) -> bool:
        """
        Delete all redirects from a channel, preserving offline times, programs and filler items

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        non_redirects = []
        for item in self.programs:
            if not helpers._object_has_attribute(obj=item, attribute_name='type') or item.type != 'redirect':
                non_redirects.append(item)
        if non_redirects and self.delete_all_programs():
            return self.add_programs(programs=non_redirects)
        return False

    @decorators.check_for_dizque_instance
    def remove_specials(self) -> bool:
        """
        Delete all specials from this channel
        Note: Removes all redirects

        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        non_redirects = [item for item in self.programs if
                         (helpers._object_has_attribute(obj=item, attribute_name='type')
                          and item.type != 'redirect')]
        non_specials = [item for item in non_redirects if
                        (helpers._object_has_attribute(obj=item, attribute_name='season')
                         and item.season != 0)]
        if non_specials and self.delete_all_programs():
            return self.add_programs(programs=non_specials)
        return False

    @decorators.check_for_dizque_instance
    def pad_times(self,
                  start_every_x_minutes: int) -> bool:
        """
        Add padding between programs on a channel, so programs start at specific intervals

        :param start_every_x_minutes: Programs start every X minutes past the hour (ex. 10 for :00, :10, :20, :30, :40 & :50; 15 for :00, :15, :30 & :45; 20 for :00, :20 & :40; 30 for :00 & :30; 60 or 0 for :00)
        :type start_every_x_minutes: int
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        programs_and_pads = []
        if self._delete_all_offline_times():
            for program in self.programs:
                filler_time_needed = helpers.get_needed_flex_time(item_time_milliseconds=program.duration,
                                                                  allowed_minutes_time_frame=start_every_x_minutes)
                programs_and_pads.append(program)
                if filler_time_needed > 0:
                    programs_and_pads.append(Program(data={'duration': filler_time_needed, 'isOffline': True},
                                                     dizque_instance=self._dizque_instance,
                                                     channel_instance=self))
            if programs_and_pads and self.delete_all_programs():
                return self.add_programs(programs=programs_and_pads)
        return False

    @decorators.check_for_dizque_instance
    def add_reruns(self,
                   start_time: datetime,
                   length_hours: int,
                   times_to_repeat: int) -> bool:
        """
        Add a block of reruns to a dizqueTV channel

        :param start_time: datetime.datetime object, what time the reruns start
        :type start_time: datetime.datetime
        :param length_hours: how long the block of reruns should be
        :type length_hours: int
        :param times_to_repeat: how many times to repeat the block of reruns
        :type times_to_repeat: int
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        if start_time > datetime.utcnow():
            raise GeneralException("You cannot use a start time in the future.")
        start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        self.remove_duplicate_programs()
        programs_to_add, running_time = helpers._get_first_x_minutes_of_programs(programs=self.programs,
                                                                                 minutes=length_hours * 60)
        if running_time < (length_hours * 60 * 60 * 1000):
            time_needed = (length_hours * 60 * 60 * 1000) - running_time
            programs_to_add.append(Program(data={'duration': time_needed, 'isOffline': True},
                                           dizque_instance=self._dizque_instance,
                                           channel_instance=self))
        final_programs_to_add = []
        for _ in range(0, times_to_repeat):
            for program in programs_to_add:
                final_programs_to_add.append(program)
        self.update(startTime=start_time)
        if final_programs_to_add and self.delete_all_programs():
            return self.add_programs(programs=final_programs_to_add)
        return False

    @decorators.check_for_dizque_instance
    def add_channel_at_night(self,
                             night_channel_number: int,
                             start_hour: int,
                             end_hour: int) -> bool:
        """
        Add a Channel at Night to a dizqueTV channel

        :param night_channel_number: number of the channel to redirect to
        :type night_channel_number: int
        :param start_hour: hour (in 24-hour time) to start the redirect
        :type start_hour: int
        :param end_hour: hour (in 24-hour time) to end the redirect
        :type end_hour: int
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        if start_hour > 23 or start_hour < 0:
            raise GeneralException("start_hour must be between 0 and 23.")
        if end_hour > 23 or end_hour < 0:
            raise GeneralException("end_hour must be between 0 and 23.")
        if start_hour == end_hour:
            raise GeneralException("You cannot add a 24-hour Channel at Night.")
        if night_channel_number not in self._dizque_instance.channel_numbers:
            raise GeneralException(f"Channel #{night_channel_number} does not exist.")
        length_of_night_block = helpers.get_milliseconds_between_two_hours(start_hour=start_hour, end_hour=end_hour)
        length_of_regular_block = (24 * 60 * 60 * 1000) - length_of_night_block
        new_channel_start_time = datetime.now().replace(hour=end_hour, minute=0, second=0, microsecond=0)
        if end_hour > datetime.now().hour:
            new_channel_start_time = new_channel_start_time - timedelta(days=1)
        new_channel_start_time = new_channel_start_time + timedelta(hours=helpers.hours_difference_in_timezone())
        new_channel_start_time = new_channel_start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        final_programs_to_add = []
        programs_left = self.programs
        while programs_left:  # loop until you get done with all the programs
            programs_to_add, total_running_time, programs_left = \
                helpers._get_first_x_minutes_of_programs_return_unused(programs=programs_left,
                                                                       minutes=int(
                                                                           length_of_regular_block / 1000 / 60)
                                                                       )
            if total_running_time < length_of_regular_block:
                # add flex time between last item and night channel
                time_needed = length_of_regular_block - total_running_time
                programs_to_add.append(Program(data={'duration': time_needed, 'isOffline': True},
                                               dizque_instance=self._dizque_instance,
                                               channel_instance=self))
            programs_to_add.append(Redirect(data={'duration': length_of_night_block,
                                                  'isOffline': True,
                                                  'channel': night_channel_number,
                                                  'type': 'redirect'},
                                            dizque_instance=self._dizque_instance,
                                            channel_instance=self))
            for program in programs_to_add:
                final_programs_to_add.append(program)

        self.update(startTime=new_channel_start_time)
        if final_programs_to_add and self.delete_all_programs():
            return self.add_programs(programs=final_programs_to_add)
        return False

    @decorators.check_for_dizque_instance
    def add_channel_at_night_alt(self,
                                 night_channel_number: int,
                                 start_hour: int,
                                 end_hour: int) -> bool:
        """
        Add a Channel at Night to a dizqueTV channel

        :param night_channel_number: number of the channel to redirect to
        :type night_channel_number: int
        :param start_hour: hour (in 24-hour time) to start the redirect
        :type start_hour: int
        :param end_hour: hour (in 24-hour time) to end the redirect
        :type end_hour: int
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        if start_hour > 23 or start_hour < 0:
            raise GeneralException("start_hour must be between 0 and 23.")
        if end_hour > 23 or end_hour < 0:
            raise GeneralException("end_hour must be between 0 and 23.")
        if night_channel_number not in self._dizque_instance.channel_numbers:
            raise GeneralException(f"Channel #{night_channel_number} does not exist.")
        length_of_night_block = helpers.get_milliseconds_between_two_hours(start_hour=start_hour, end_hour=end_hour)
        if length_of_night_block == 0:
            raise GeneralException("You cannot add a 24-hour Channel at Night.")
        length_of_regular_block = (24 * 60 * 60 * 1000) - length_of_night_block
        channel_start_time_datetime = helpers.string_to_datetime(date_string=self.startTime)
        time_until_night_block_start = helpers.get_milliseconds_between_two_datetimes(
            start_datetime=helpers.adjust_datetime_for_timezone(channel_start_time_datetime),
            end_datetime=datetime.now().replace(hour=start_hour,
                                                minute=0,
                                                second=0,
                                                microsecond=0)
        )
        final_programs_to_add = []
        all_programs = self.programs
        programs_to_add, total_running_time = helpers._get_first_x_minutes_of_programs(
            programs=all_programs,
            minutes=int(
                time_until_night_block_start / 1000 / 60)
        )
        if len(programs_to_add) == len(all_programs):  # all programs can play before night channel even starts
            if total_running_time < time_until_night_block_start:  # add flex time between last item and night channel
                time_needed = time_until_night_block_start - total_running_time
                programs_to_add.append(Program(data={'duration': time_needed, 'isOffline': True},
                                               dizque_instance=self._dizque_instance,
                                               channel_instance=self))
            # add the night channel
            programs_to_add.append(Redirect(data={'duration': length_of_night_block,
                                                  'isOffline': True,
                                                  'channel': night_channel_number,
                                                  'type': 'redirect'},
                                            dizque_instance=self._dizque_instance,
                                            channel_instance=self))
            final_programs_to_add = programs_to_add
        else:  # need to interlace programs and night channels
            programs_left = all_programs
            programs_to_add, total_running_time, programs_left = \
                helpers._get_first_x_minutes_of_programs_return_unused(programs=programs_left,
                                                                       minutes=int(
                                                                           time_until_night_block_start / 1000 / 60)
                                                                       )
            if total_running_time < time_until_night_block_start:  # add flex time between last item and night channel
                time_needed = time_until_night_block_start - total_running_time
                programs_to_add.append(Program(data={'duration': time_needed, 'isOffline': True},
                                               dizque_instance=self._dizque_instance,
                                               channel_instance=self))
            # add the night channel
            programs_to_add.append(Redirect(data={'duration': length_of_night_block,
                                                  'isOffline': True,
                                                  'channel': night_channel_number,
                                                  'type': 'redirect'},
                                            dizque_instance=self._dizque_instance,
                                            channel_instance=self))
            final_programs_to_add = programs_to_add
            while programs_left:  # loop until you get done with all the programs
                programs_to_add, total_running_time, programs_left = \
                    helpers._get_first_x_minutes_of_programs_return_unused(programs=programs_left,
                                                                           minutes=int(
                                                                               length_of_regular_block / 1000 / 60)
                                                                           )
                if total_running_time < length_of_regular_block:
                    # add flex time between last item and night channel
                    time_needed = length_of_regular_block - total_running_time
                    programs_to_add.append(Program(data={'duration': time_needed, 'isOffline': True},
                                                   dizque_instance=self._dizque_instance,
                                                   channel_instance=self))
                programs_to_add.append(Redirect(data={'duration': length_of_night_block,
                                                      'isOffline': True,
                                                      'channel': night_channel_number,
                                                      'type': 'redirect'},
                                                dizque_instance=self._dizque_instance,
                                                channel_instance=self))
                for program in programs_to_add:
                    final_programs_to_add.append(program)
        if final_programs_to_add and self.delete_all_programs():
            return self.add_programs(programs=final_programs_to_add)
        return False

    @decorators.check_for_dizque_instance
    def balance_programs(self,
                         margin_of_error: float = 0.1) -> bool:
        """
        Balance shows to the shortest show length. Movies unaffected.

        :param margin_of_error: (Optional) Specify margin of error when deciding whether to add another episode. Ex. margin_of_error = 0.1 -> If adding a new episode would eclipse the shortest show length by 10% or less, add the episode.
        :type margin_of_error: float, optional
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.balance_shows(media_items=self.programs, margin_of_correction=margin_of_error)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def fast_forward(self,
                     seconds: int = 0,
                     minutes: int = 0,
                     hours: int = 0,
                     days: int = 0,
                     months: int = 0,
                     years: int = 0) -> bool:
        """
        Fast forward the channel start time by an amount of time

        :param seconds: how many seconds
        :type seconds: int, optional
        :param minutes: how many minutes
        :type minutes: int, optional
        :param hours: how many hours
        :type hours: int, optional
        :param days: how many days
        :type days: int, optional
        :param months: how many months (assume 30 days in month)
        :type months: int, optional
        :param years: how many years (assume 365 days in year)
        :type years: int, optional
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        current_start_time = helpers.string_to_datetime(date_string=self.startTime)
        shifted_start_time = helpers.shift_time(starting_time=current_start_time,
                                                seconds=seconds,
                                                minutes=minutes,
                                                hours=hours,
                                                days=days,
                                                months=months,
                                                years=years)
        shifted_start_time = helpers.datetime_to_string(datetime_object=shifted_start_time)
        if self.update(startTime=shifted_start_time):
            return True
        return False

    @decorators.check_for_dizque_instance
    def rewind(self,
               seconds: int = 0,
               minutes: int = 0,
               hours: int = 0,
               days: int = 0,
               months: int = 0,
               years: int = 0) -> bool:
        """
        Fast forward the channel start time by an amount of time

        :param seconds: how many seconds
        :type seconds: int, optional
        :param minutes: how many minutes
        :type minutes: int, optional
        :param hours: how many hours
        :type hours: int, optional
        :param days: how many days
        :type days: int, optional
        :param months: how many months (assume 30 days in month)
        :type months: int, optional
        :param years: how many years (assume 365 days in year)
        :type years: int, optional
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        return self.fast_forward(seconds=seconds * -1,
                                 minutes=minutes * -1,
                                 hours=hours * -1,
                                 days=days * -1,
                                 months=months * -1,
                                 years=years * -1)

    # Delete
    @decorators.check_for_dizque_instance
    def delete(self) -> bool:
        """
        Delete this channel

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        return self._dizque_instance.delete_channel(channel_number=self.number)
