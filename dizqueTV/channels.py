import json
from typing import List, Union, Tuple
from datetime import datetime, timedelta

from plexapi.video import Video, Movie, Episode
from plexapi.server import PlexServer as PServer

import dizqueTV.helpers as helpers
from dizqueTV.fillers import FillerList
from dizqueTV.media import Redirect, Program, FillerItem
from dizqueTV.templates import MOVIE_PROGRAM_TEMPLATE, EPISODE_PROGRAM_TEMPLATE, \
    REDIRECT_PROGRAM_TEMPLATE, FILLER_LIST_SETTINGS_TEMPLATE, FILLER_LIST_CHANNEL_TEMPLATE
from dizqueTV.exceptions import MissingParametersError


class Channel:
    def __init__(self, data: json, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self._program_data = data.get('programs')
        self._fillerCollections_data = data.get('fillerCollections')
        self.fillerRepeatCooldown = data.get('fillerRepeatCooldown')
        self.fallback = [FillerItem(data=filler_data, dizque_instance=dizque_instance, filler_list_instance=None)
                         for filler_data in data.get('fallback')]
        self.icon = data.get('icon')
        self.disableFillerOverlay = data.get('disableFillerOverlay')
        self.iconWidth = data.get('iconWidth')
        self.iconDuration = data.get('iconDuration')
        self.iconPosition = data.get('iconPosition')
        self.overlayIcon = data.get('overlayIcon')
        self.startTime = data.get('startTime')
        self.offlinePicture = data.get('offlinePicture')
        self.offlineSoundtrack = data.get('offlineSoundtrack')
        self.offlineMode = data.get('offlineMode')
        self.number = data.get('number')
        self.name = data.get('name')
        self.duration = data.get('duration')
        self.stealth = data.get('stealth')
        self._id = data.get('_id')

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.number}:{self.name}>"

    # CRUD Operations
    # Create (handled in dizqueTV.py)
    # Read
    @property
    def programs(self):
        """
        Get all programs on this channel
        :return: List of MediaItem objects
        """
        return [Program(data=program, dizque_instance=self._dizque_instance, channel_instance=self)
                for program in self._program_data]

    @helpers._check_for_dizque_instance
    def get_program(self, program_title: str = None, redirect_channel_number: int = None) -> Union[Program, None]:
        """
        Get a specific program on this channel
        :param program_title: Title of program
        :param redirect_channel_number: Channel number for Redirect object (use if getting Redirect instead of Program)
        :return: Program object or None
        """
        if not program_title and not redirect_channel_number:
            raise MissingParametersError("Please include either a program_title or a redirect_channel_number.")
        for program in self.programs:
            if (program_title and program.title == program_title) \
                    or (redirect_channel_number and redirect_channel_number == program.channel):
                return program
        return None

    @property
    def filler_lists(self):
        """
        Get all filler lists on this channel
        :return: List of FillerList objects
        """
        return [FillerList(data=filler_list, dizque_instance=self._dizque_instance)
                for filler_list in self._fillerCollections_data]

    @helpers._check_for_dizque_instance
    def get_filler_list(self, filler_list_title: str) -> Union[FillerList, None]:
        """
        Get a specific filler list on this channel
        :param filler_list_title: Title of filler list
        :return: FillerList object or None
        """
        for filler_list in self.filler_lists:
            if filler_list.name == filler_list_title:
                return filler_list
        return None

    # Update
    @helpers._check_for_dizque_instance
    def refresh(self):
        """
        Reload current Channel object
        Use to update program and filler data
        """
        temp_channel = self._dizque_instance.get_channel(channel_number=self.number)
        if temp_channel:
            json_data = temp_channel._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_channel

    @helpers._check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit this Channel on dizqueTV
        Automatically refreshes current Channel object
        :param kwargs: keyword arguments of Channel settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        if self._dizque_instance.update_channel(channel_number=self.number, **kwargs):
            self.refresh()
            return True
        return False

    @helpers._check_for_dizque_instance
    def add_program(self,
                    plex_item: Union[Video, Movie, Episode] = None,
                    plex_server: PServer = None,
                    program: Program = None,
                    **kwargs) -> bool:
        """
        Add a program to this channel
        :param plex_item: plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode object (optional)
        :param plex_server: plexapi.server.PlexServer object (optional)
        :param program: Program object (optional)
        :param kwargs: keyword arguments of Program settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in place)
        """
        if not plex_item and not program and not kwargs:
            raise MissingParametersError("Please include either a program, a plex_item/plex_server combo, or kwargs")
        if plex_item and plex_server:
            temp_program = self._dizque_instance.convert_plex_item_to_program(plex_item=plex_item,
                                                                              plex_server=plex_server)
            kwargs = temp_program._data
        elif program:
            kwargs = program._data
        template = MOVIE_PROGRAM_TEMPLATE
        if kwargs['type'] == 'episode':
            template = EPISODE_PROGRAM_TEMPLATE
        elif kwargs['type'] == 'redirect':
            template = REDIRECT_PROGRAM_TEMPLATE
        if helpers._settings_are_complete(new_settings_dict=kwargs,
                                          template_settings_dict=template,
                                          ignore_id=True):
            channel_data = self._data
            channel_data['programs'].append(kwargs)
            channel_data['duration'] += kwargs['duration']
            return self.update(**channel_data)
        return False

    @helpers._check_for_dizque_instance
    def add_programs(self, programs: List[Union[Program, Video, Movie, Episode]], plex_server: PServer = None) -> bool:
        """
        Add multiple programs to this channel
        :param programs: List of Program, plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode objects
        :param plex_server: plexapi.server.PlexServer object
        (required if adding PlexAPI Video, Movie or Episode objects)
        :return: True if successful, False if unsuccessful (Channel reloads in place)
        """
        channel_data = self._data
        if not programs:
            raise Exception("You must provide at least one program to add to the channel.")
        for program in programs:
            if type(program) not in [Program, Redirect]:
                if not plex_server:
                    raise MissingParametersError("Please include a plex_server if you are adding PlexAPI Video, "
                                                 "Movie, or Episode items.")
                program = self._dizque_instance.convert_plex_item_to_program(plex_item=program, plex_server=plex_server)
            channel_data['programs'].append(program._data)
            channel_data['duration'] += program.duration
        return self.update(**channel_data)

    @helpers._check_for_dizque_instance
    def delete_program(self, program: Program) -> bool:
        """
        Delete a program from this channel
        :param program: Program object to delete
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        channel_data = self._data
        for a_program in channel_data['programs']:
            if (program.type == 'redirect' and a_program['type'] == 'redirect') \
                    or (a_program['title'] == program.title):
                channel_data['duration'] -= a_program['duration']
                channel_data['programs'].remove(a_program)
                return self.update(**channel_data)
        return False

    @helpers._check_for_dizque_instance
    def delete_show(self, show_name: str, season_number: int = None) -> bool:
        """
        Delete all episodes of a specific show
        :param show_name: Name of show to delete
        :param season_number: (Optional) Number of season to delete
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        all_programs = self.programs
        programs_to_add = []
        for program in all_programs:
            if program.type == 'episode' and program.showTitle == show_name:
                if season_number and program.season == season_number:
                    pass
                else:
                    programs_to_add.append(program)
            else:
                programs_to_add.append(program)
        if self.delete_all_programs():
            return self.add_programs(programs=programs_to_add)
        return False

    @helpers._check_for_dizque_instance
    def delete_all_programs(self) -> bool:
        """
        Delete all programs from this channel
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        channel_data = self._data
        channel_data['duration'] -= sum(program.duration for program in self.programs)
        channel_data['programs'] = []
        return self.update(**channel_data)

    @helpers._check_for_dizque_instance
    def _delete_all_offline_times(self) -> bool:
        """
        Delete all offline program in a channel
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        programs_to_add = []
        for program in self.programs:
            if not program.isOffline or program.type == 'redirect':
                programs_to_add.append(program)
        if programs_to_add and self.delete_all_programs():
            return self.add_programs(programs=programs_to_add)
        return False

    @helpers._check_for_dizque_instance
    def add_filler_list(self,
                        filler_list: FillerList = None,
                        filler_list_id: str = None,
                        weight: int = 300,
                        cooldown: int = 0) -> bool:
        """
        Add a filler list to this channel
        :param filler_list: FillerList object (optional)
        :param filler_list_id: ID of FillerList (optional)
        :param weight: weight to assign list in channel (default: 300)
        :param cooldown: cooldown to assign list in channel (default: 0)
        :return: True if successful, False if unsuccessful (Channel reloads in place)
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
                                          ignore_id=False):
            channel_data = self._data
            channel_data['fillerCollections'].append(new_settings_dict)
            # filler_list_data['duration'] += kwargs['duration']
            return self.update(**channel_data)
        return False

    @helpers._check_for_dizque_instance
    def delete_filler_list(self, filler_list: FillerList = None, filler_list_id: str = None) -> bool:
        """
        Delete a program from this channel
        :param filler_list: FillerList object to delete
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        if not filler_list and not filler_list_id:
            raise Exception("You must include either a filler_list or a filler_list_id.")
        if filler_list:
            filler_list_id = filler_list.id
        channel_data = self._data
        for a_list in channel_data['fillerCollections']:
            if filler_list_id == a_list.get('id'):
                channel_data['fillerCollections'].remove(a_list)
                return self.update(**channel_data)
        return False

    @helpers._check_for_dizque_instance
    def delete_all_filler_lists(self):
        """
        Delete all filler lists from this channel
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        channel_data = self._data
        channel_data['fillerCollections'] = []
        return self.update(**channel_data)

    # Sort Programs
    @helpers._check_for_dizque_instance
    def sort_programs_by_release_date(self) -> bool:
        """
        Sort all programs on this channel by release date
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        sorted_programs = helpers.sort_media_by_release_date(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @helpers._check_for_dizque_instance
    def sort_programs_by_season_order(self) -> bool:
        """
        Sort all programs on this channel by season order
        Movies are added at the end of the list
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        sorted_programs = helpers.sort_media_by_season_order(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @helpers._check_for_dizque_instance
    def sort_programs_alphabetically(self) -> bool:
        """
        Sort all programs on this channel in alphabetical order
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        sorted_programs = helpers.sort_media_alphabetically(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @helpers._check_for_dizque_instance
    def sort_programs_by_duration(self) -> bool:
        """
        Sort all programs on this channel by duration
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        sorted_programs = helpers.sort_media_by_duration(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @helpers._check_for_dizque_instance
    def sort_programs_randomly(self) -> bool:
        """
        Sort all programs on this channel randomly
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        sorted_programs = helpers.sort_media_randomly(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @helpers._check_for_dizque_instance
    def cyclical_shuffle(self) -> bool:
        """
        Sort TV shows on this channel cyclically
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        sorted_programs = helpers.sort_media_cyclical_shuffle(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @helpers._check_for_dizque_instance
    def block_shuffle(self, block_length: int, randomize: bool = False) -> bool:
        """
        Sort TV shows on this channel cyclically
        :param block_length: Length of each block
        :param randomize: Random block lengths between 1 and block_length
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        sorted_programs = helpers.sort_media_block_shuffle(media_items=self.programs,
                                                           block_length=block_length,
                                                           randomize=randomize)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @helpers._check_for_dizque_instance
    def replicate(self, how_many_times: int) -> bool:
        """
        Replicate/repeat the channel lineup x number of times
        Items will remain in the same order.
        Ex. [A, B, C] x3 -> [A, B, C, A, B, C, A, B, C]
        :param how_many_times: how many times to repeat the lineup
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        programs = self.programs
        final_program_list = []
        for _ in range(0, how_many_times):
            for program in programs:
                final_program_list.append(program)
        if final_program_list and self.delete_all_programs():
            return self.add_programs(programs=final_program_list)
        return False

    @helpers._check_for_dizque_instance
    def replicate_and_shuffle(self, how_many_times: int) -> bool:
        """
        Replicate/repeat the channel lineup, shuffled, x number of times
        Items will be shuffled in each repeat group.
        Ex. [A, B, C] x3 -> [A, B, C, B, A, C, C, A, B]
        :param how_many_times: how many times to repeat the lineup
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
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

    @helpers._check_for_dizque_instance
    def remove_duplicate_programs(self) -> bool:
        """
        Delete duplicate programs on this channel
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        sorted_programs = helpers.remove_duplicate_media_items(media_items=self.programs)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @helpers._check_for_dizque_instance
    def remove_specials(self) -> bool:
        """
        Delete all specials from this channel
        Note: Removes all redirects
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        non_redirects = [item for item in self.programs if
                         (helpers._object_has_attribute(object=item, attribute_name='type')
                          and item.type != 'redirect')]
        non_specials = [item for item in non_redirects if
                        (helpers._object_has_attribute(object=item, attribute_name='season')
                         and item.season != 0)]
        if non_specials and self.delete_all_programs():
            return self.add_programs(programs=non_specials)
        return False

    @helpers._check_for_dizque_instance
    def pad_times(self, start_every_x_minutes: int) -> bool:
        """
        Add padding between programs on a channel, so programs start at specific intervals
        :param start_every_x_minutes: Programs start every X minutes past the hour
        (ex.
        10 for :00, :10, :20, :30, :40 & :50
        15 for :00, :15, :30 & :45
        20 for :00, :20 & :40
        30 for :00 & :30
        60 or 0 for :00)
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
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

    @helpers._check_for_dizque_instance
    def add_reruns(self, start_time: datetime, length_hours: int, times_to_repeat: int) -> bool:
        """
        Add a block of reruns to a dizqueTV channel
        :param start_time: datetime.datetime object, what time the reruns start
        :param length_hours: how long the block of reruns should be
        :param times_to_repeat: how many times to repeat the block of reruns
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        if start_time > datetime.utcnow():
            raise Exception("You cannot use a start time in the future.")
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

    @helpers._check_for_dizque_instance
    def add_channel_at_night(self, night_channel_number: int, start_hour: int, end_hour: int) -> bool:
        """
        Add a Channel at Night to a dizqueTV channel
        :param night_channel_number: number of the channel to redirect to
        :param start_hour: hour (in 24-hour time) to start the redirect
        :param end_hour: hour (in 24-hour time) to end the redirect
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        if start_hour > 23 or start_hour < 0:
            raise Exception("start_hour must be between 0 and 23.")
        if end_hour > 23 or end_hour < 0:
            raise Exception("end_hour must be between 0 and 23.")
        if start_hour == end_hour:
            raise Exception("You cannot add a 24-hour Channel at Night.")
        if night_channel_number not in self._dizque_instance.channel_numbers:
            raise Exception(f"Channel #{night_channel_number} does not exist.")
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

    @helpers._check_for_dizque_instance
    def add_channel_at_night_alt(self, night_channel_number: int, start_hour: int, end_hour: int) -> bool:
        if start_hour > 23 or start_hour < 0:
            raise Exception("start_hour must be between 0 and 23.")
        if end_hour > 23 or end_hour < 0:
            raise Exception("end_hour must be between 0 and 23.")
        if night_channel_number not in self._dizque_instance.channel_numbers:
            raise Exception(f"Channel #{night_channel_number} does not exist.")
        length_of_night_block = helpers.get_milliseconds_between_two_hours(start_hour=start_hour, end_hour=end_hour)
        if length_of_night_block == 0:
            raise Exception("You cannot add a 24-hour Channel at Night.")
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
        programs_to_add, total_running_time = helpers._get_first_x_minutes_of_programs(programs=all_programs,
                                                                                       minutes=int(
                                                                                           time_until_night_block_start /
                                                                                           1000 / 60)
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

    @helpers._check_for_dizque_instance
    def balance_programs(self, margin_of_error: float = 0.1) -> bool:
        """
        Balance shows to the shortest show length. Movies unaffected.
        :param margin_of_error: (Optional) Specify margin of error when deciding whether to add another episode.
        Ex. margin_of_error = 0.1 -> If adding a new episode would eclipse the shortest show length by 10% or less,
        add the episode.
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        """
        sorted_programs = helpers.balance_shows(media_items=self.programs, margin_of_correction=margin_of_error)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    # Delete
    @helpers._check_for_dizque_instance
    def delete(self) -> bool:
        """
        Delete this channel
        :return: True if successful, False if unsuccessful
        """
        return self._dizque_instance.delete_channel(channel_number=self.number)
