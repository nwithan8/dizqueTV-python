from typing import Union, List

from plexapi.audio import Track
from plexapi.server import PlexServer as PServer
from plexapi.video import Video, Movie, Episode

from dizqueTV import decorators, helpers
from dizqueTV.exceptions import MissingParametersError, ItemCreationError
from dizqueTV.models.base import BaseAPIObject
from dizqueTV.models.media import Program


class CustomShowItem(Program):
    def __init__(self, data: dict, dizque_instance, order: int):
        super().__init__(data, dizque_instance, None)
        self._full_data = data
        self.order = order
        self.durationStr = data.get('durationStr')
        self._commercials = []

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title})"

    @property
    def _data(self):
        """
        Override default self._data to ignore durationStr and commercials

        :return: Data dict
        :rtype: dict
        """
        data = self._full_data
        data.pop('durationStr', None)
        data.pop('commercials', None)
        return data

    @property
    def commercials(self) -> List:
        """
        Get the show's commercials

        :return: List of commercials
        :rtype: list
        """
        if not self._commercials:
            self._commercials = []
        return self._commercials


class CustomShowDetails(BaseAPIObject):
    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.name = data.get('name')
        self.id = data.get('id')
        self._content = []

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    @property
    def content(self) -> List[CustomShowItem]:
        """
        Get the custom show's content (the actual programs)

        :return: list of CustomShowItem objects
        :rtype: list
        """
        if not self._content:
            order = 0
            for item in self._data.get('content', []):
                self._content.append(CustomShowItem(data=item, dizque_instance=self._dizque_instance, order=order))
                order += 1
        return self._content


class CustomShow(BaseAPIObject):
    # Has no knowledge of the Channel or FillerList it belongs to

    def __init__(self, data: dict, dizque_instance):
        super().__init__(data, dizque_instance)
        self.id = data.get('id')
        self.name = data.get('name')
        self.count = data.get('count')
        self.type = "customShow"
        self.customShowTag = "customShow"
        self._details = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    @property
    def details(self) -> Union[CustomShowDetails, None]:
        """
        Get the custom show's details

        :return: CustomShowDetails object
        :rtype: CustomShowDetails
        """
        if not self._details:
            self._details = self._dizque_instance.get_custom_show_details(custom_show_id=self.id)
        return self._details

    @property
    def content(self) -> List[CustomShowItem]:
        """
        Get the custom show's content (the actual programs)

        :return: list of CustomShowItem objects
        :rtype: list
        """
        details = self.details
        if not details:
            return []
        return details.content

    # Update
    @decorators.check_for_dizque_instance
    def refresh(self):
        """
        Reload current CustomShow object
        Use to update program data

        :return: None
        """
        temp_custom_show = self._dizque_instance.get_custom_show(custom_show_id=self.id)
        if temp_custom_show:
            json_data = temp_custom_show._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_custom_show

    @decorators.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit this CustomShow on dizqueTV
        Automatically refreshes current CustomShow object

        :param kwargs: keyword arguments of CustomShow settings names and values
        :return: True if successful, False if unsuccessful (CustomShow reloads in-place)
        :rtype: bool
        """
        if self._dizque_instance.update_custom_show(custom_show_id=self.id, **kwargs):
            self.refresh()
            return True
        return False

    @decorators.check_for_dizque_instance
    def edit(self,
             **kwargs) -> bool:
        """
        Alias for custom_show.update()

        :param kwargs: keyword arguments of CustomShow settings names and values
        :return: True if successful, False if unsuccessful (Channel reloads in-place)
        :rtype: bool
        """
        return self.update(**kwargs)

    @decorators.check_for_dizque_instance
    def add_program(self,
                    plex_item: Union[Video, Movie, Episode, Track] = None,
                    plex_server: PServer = None,
                    program: Union[Program, CustomShowItem] = None):
        """
        Add a program to this custom show

        :param plex_item: plexapi.video.Video, plexapi.video.Moviem plexapi.video.Episode or plexapi.audio.Track object (optional)
        :type plex_item: Union[plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode, plexapi.audio.Track], optional
        :param plex_server: plexapi.server.PlexServer object (optional)
        :type plex_server: plexapi.server.PlexServer, optional
        :param program: Program or CustomShowItem object (optional)
        :type program: Union[Program, CustomShowItem], optional
        :return: True if successful, False if unsuccessful (CustomShow reloads in place)
        :rtype: bool
        """
        custom_show_data = self._data

        if not plex_item and not program:
            raise MissingParametersError("Please include either a program, a plex_item/plex_server combo, or kwargs")
        if plex_item:
            if not plex_server:
                raise ItemCreationError("You must include a plex_server if you are adding PlexAPI Videos, "
                                        "Movies, Episodes or Tracks as programs")
            program = self._dizque_instance.convert_plex_item_to_program(plex_item=plex_item, plex_server=plex_server)
            custom_show_item = self._dizque_instance.convert_program_to_custom_show_item(program=program)
        elif type(program) != CustomShowItem:
            custom_show_item = self._dizque_instance.convert_program_to_custom_show_item(program=program)
        else:
            custom_show_item = program
        custom_show_data['content'].append(custom_show_item._full_data)
        custom_show_data['count'] = len(custom_show_data['content'])
        if custom_show_data.get('duration'):
            custom_show_data['duration'] += custom_show_item.duration
        return self.update(**custom_show_data)

    @decorators.check_for_dizque_instance
    def add_programs(self,
                     programs: List[Union[Program, CustomShowItem, Video, Movie, Episode, Track]] = None,
                     plex_server: PServer = None):
        """
        Add multiple programs to this custom show

        :param programs: List of Program, CustomShowItem, plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode or plexapi.audio.Track objects
        :type programs: List[Union[Program, CustomShowItem, plexapi.video.Video, plexapi.video.Movie, plexapi.video.Episode, plexapi.audio.Track]]
        :param plex_server: plexapi.server.PlexServer object (required if adding PlexAPI Video, Movie, Episode or Track objects)
        :type plex_server: plexapi.server.PlexServer, optional
        :return: True if successful, False if unsuccessful (CustomShow reloads in place)
        :rtype: bool
        """

        custom_show_data = self._data

        for program in programs:
            if type(program) not in [Program, CustomShowItem]:
                if not plex_server:
                    raise MissingParametersError("Please include a plex_server if you are adding PlexAPI Video, "
                                                 "Movie, Episode or Track items.")
                temp_program = self._dizque_instance.convert_plex_item_to_program(plex_item=program,
                                                                                  plex_server=plex_server)
                custom_show_item = self._dizque_instance.convert_program_to_custom_show_item(program=temp_program)
            elif type(program) != CustomShowItem:
                custom_show_item = self._dizque_instance.convert_program_to_custom_show_item(program=program)
            else:
                custom_show_item = program
            custom_show_data['content'].append(custom_show_item._full_data)
            custom_show_data['count'] = len(custom_show_data['content'])
            if custom_show_data.get('duration'):
                custom_show_data['duration'] += custom_show_item.duration
        return self.update(**custom_show_data)

    @decorators.check_for_dizque_instance
    def delete_program(self, program: Union[Program, CustomShowItem]) -> bool:
        """
        Delete a custom show item from this custom show

        :param program: CustomShowItem or Program object to delete
        :type program: CustomShowItem or Program
        :return: True if successful, False if unsuccessful (CustomShow reloads in-place)
        :rtype: bool
        """
        custom_show_data = self._data
        for a_program in custom_show_data['content']:
            if a_program['title'] == program.title:
                if custom_show_data.get('duration'):
                    custom_show_data['duration'] -= a_program['duration']
                custom_show_data['content'].remove(a_program)
                return self.update(**custom_show_data)
        return False

    @decorators.check_for_dizque_instance
    def delete_all_programs(self) -> bool:
        """
        Delete all custom show items from this custom show

        :return: True if successful, False if unsuccessful (CustomShow reloads in-place)
        :rtype: bool
        """
        custom_show_data = self._data
        if custom_show_data.get('duration'):
            custom_show_data['duration'] -= sum(program.duration for program in self.content)
        custom_show_data['content'] = []
        return self.update(**custom_show_data)

    # Sort FillerItem
    @decorators.check_for_dizque_instance
    def sort_filler_by_duration(self) -> bool:
        """
        Sort all custom show items on this custom show by duration

        :return: True if successful, False if unsuccessful (CustomShow reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.sort_media_by_duration(media_items=self.content)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def sort_filler_randomly(self) -> bool:
        """
        Sort all custom show items on this custom show randomly

        :return: True if successful, False if unsuccessful (CustomShow reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.sort_media_randomly(media_items=self.content)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    @decorators.check_for_dizque_instance
    def remove_duplicate_fillers(self) -> bool:
        """
        Delete duplicate custom show items on this custom show

        :return: True if successful, False if unsuccessful (CustomShow reloads in-place)
        :rtype: bool
        """
        sorted_programs = helpers.remove_duplicate_media_items(media_items=self.content)
        if sorted_programs and self.delete_all_programs():
            return self.add_programs(programs=sorted_programs)
        return False

    # Delete
    @decorators.check_for_dizque_instance
    def delete(self) -> bool:
        """
        Delete this custom show

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        return self._dizque_instance.delete_custom_show(custom_show_id=self.id)
