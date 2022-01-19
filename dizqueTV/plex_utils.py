from typing import List, Union

from plexapi import server, media, library, playlist, myplex


class PlexUtils:
    def __init__(self, url: str, token: str):
        """
        Work with the Plex API

        :param url: Plex Media Server url
        :type url: str
        :param token: Plex Media Server token
        :type token: str
        """
        if not url or not token:
            raise ValueError("url and token must be set")
        self.server = server.PlexServer(url, token)

    @property
    def users(self) -> List[myplex.MyPlexUser]:
        """
        Get all users on a Plex Media Server

        :return: List of Plex users
        :rtype: list[plexapi.myplex.MyPlexUser]
        """
        return self.server.myPlexAccount().users()

    @property
    def playlists(self) -> List[playlist.Playlist]:
        """
        Get all playlists on a Plex Media Server

        :return: List of Plex playlists
        :rtype: list[plexapi.playlist.Playlist]
        """
        return self.server.playlists()

    @property
    def library_sections(self) -> List[library.LibrarySection]:
        """
        Get all library sections on a Plex Media Server

        :return: list of Plex library sections
        :rtype: list[plexapi.library.LibrarySection]
        """
        return self.server.library.sections()

    def user_has_server_access(self, user: myplex.MyPlexUser) -> bool:
        """
        Check if a user has access to a Plex Media Server

        :param user: User to check access for
        :type user: plexapi.myplex.MyPlexUser
        :return: True if user has access, False if user does not have access
        :rtype: bool
        """
        for s in user.servers:
            if s.name == self.server.friendlyName:
                return True
        return False

    def get_playlist(self, playlist_name: str) -> Union[playlist.Playlist, None]:
        """
        Get a specific Plex playlist

        :param playlist_name: Name of the Plex playlist
        :type playlist_name: str
        :return: Plex playlist or None
        :rtype: plexapi.playlist.Playlist | None
        """
        for playlist in self.playlists:
            if playlist.title == playlist_name:
                return playlist
        return None

    def create_new_playlist(self, playlist_name: str, items: List[media.Media]) -> bool:
        """
        Create a new Plex playlist

        :param playlist_name: Name of the new Plex playlist
        :type playlist_name: str
        :param items: List of items to add to the playlist
        :type items: list[plexapi.media.Media]
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        try:
            self.server.createPlaylist(title=playlist_name, items=items)
            return True
        except:
            return False

    def reset_playlist(self, playlist_name: str, items: List[media.Media]) -> bool:
        """
        Reset a Plex playlist (recreate it with new content)

        :param playlist_name: Name of the Plex playlist
        :type playlist_name: str
        :param items: List of items to add to the playlist
        :type items: list[plexapi.media.Media]
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        try:
            playlist = self.get_playlist(playlist_name=playlist_name)
            if playlist:
                playlist.delete()
            self.create_new_playlist(playlist_name=playlist_name, items=items)
            return True
        except:
            return False

    def get_all_section_items(self, section: library.LibrarySection) -> List[media.Media]:
        """
        Get all Plex media items in a specific library section
        NOTE: May be slow on large library sections

        :param section: Plex library section to load items from
        :type section: plexapi.library.LibrarySection
        :return: List of Plex media items
        :rtype: list[plexapi.media.Media]
        """
        return section.all()

    def search_for_plex_items(self, section_name: str = None, result_class: type = None, **search_terms) -> List[
        media.Media]:
        """
        Search for Plex items

        :param section_name: Name of section to search in, optional
        :type section_name: str
        :param result_class: Type of item to search for, optional
        :type result_class: Any
        :param search_terms: keyword arguments of search parameters
        :return: List of matching Plex media items
        :rtype: List[plexapi.media.Media]
        """
        if section_name:
            results = self.server.library.section(section_name).search(**search_terms)
        else:
            results = self.server.library.search(**search_terms)
        if result_class:
            return [item for item in results if isinstance(item, result_class)]
        return results

    def search_for_plex_items_with_advanced_filters(self, section_name: str = None, result_class: type = None, **search_terms) -> List[media.Media]:
        """
        Search for Plex items

        :param section_name: Name of section to search in, optional
        :type section_name: str
        :param result_class: Type of item to search for, optional
        :type result_class: Any
        :param search_terms: keyword arguments of search parameters
        :return: List of matching Plex media items
        :rtype: List[plexapi.media.Media]
        """
        return self.search_for_plex_items(section_name=section_name, result_class=result_class, **{'filters': search_terms})

    def get_dizque_item_on_plex(self, dizque_item, section_name: str = None) -> Union[media.Media, None]:
        """
        Locate a dizqueTV item on Plex

        :param dizque_item: dizqueTV item to find on Plex
        :param section_name: Name of Plex library section to search for item, optional
        :type section_name: str
        :return: Matching Plex media item or None
        :rtype: plexapi.media.Media | None
        """
        if section_name:
            results = self.server.library.section(section_name).search(title=dizque_item.title)
        else:
            results = self.server.library.search(title=dizque_item.title)
        for plex_item in results:
            if plex_item.ratingKey and int(plex_item.ratingKey) == int(dizque_item.ratingKey):
                return plex_item
        return None


class PlexSearch(PlexUtils):
    def __init__(self, url: str = None, token: str = None, plex_server: server.PlexServer = None):
        if not plex_server:
            super().__init__(url=url, token=token)
        else:
            self.server = plex_server

    def _search_by_any_match_query_in_sections(self, query_key: str, query_values: list, section_names: List[str] = None) -> List[media.Media]:
        matches = []
        if not section_names:
            section_names = [None]

        for section_name in section_names:
            for query_value in query_values:
                matches.extend(self.search_for_plex_items(section_name=section_name, **{query_key: query_value}))
        return list(set(matches))

    def _search_by_any_advanced_filter_match_query_in_sections(self, query_key: str, query_values: list, section_names: List[str] = None) -> List[media.Media]:
        matches = []
        if not section_names:
            section_names = [None]

        for section_name in section_names:
            for query_value in query_values:
                matches.extend(
                    self.search_for_plex_items_with_advanced_filters(section_name=section_name, **{query_key: query_value}))
        return list(set(matches))

    def search_by_any_keywords_in_summary(self, keywords: List[str], section_names: List[str] = None) -> List[
        media.Media]:
        """
        Find Plex media items with any of the keywords in their summary

        :param keywords: List of keywords to search for. If any of these keywords are found in the summary, the item is considered a match.
        :type keywords: List[str]
        :param section_names: Names of Plex library sections to search for item, optional
        :type section_names: List[str]
        :return: Matching Plex media item or None
        :rtype: plexapi.media.Media | None
        """
        return self._search_by_any_match_query_in_sections(query_key='summary__icontains', query_values=keywords, section_names=section_names)

    def search_by_any_keyword_in_title(self, keywords: List[str], section_names: List[str] = None) -> List[media.Media]:
        """
        Find Plex media items with any of the keywords in their title

        :param keywords: List of keywords to search for. If any of these keywords are found in the title, the item is considered a match.
        :type keywords: List[str]
        :param section_names: Names of Plex library sections to search for item, optional
        :type section_names: List[str]
        :return: Matching Plex media item or None
        :rtype: plexapi.media.Media | None
        """
        return self._search_by_any_match_query_in_sections(query_key='title__icontains', query_values=keywords, section_names=section_names)

    def search_by_genre(self, genres: List[str], section_names: List[str] = None) -> List[media.Media]:
        """
        Find Plex media items with any of the keywords in their title

        :param genres: List of genres to search for. If any of these genres are found on the item, the item is considered a match.
        :type genres: List[str]
        :param section_names: Names of Plex library sections to search for item, optional
        :type section_names: List[str]
        :return: Matching Plex media item or None
        :rtype: plexapi.media.Media | None
        """
        return self._search_by_any_advanced_filter_match_query_in_sections(query_key='genre&', query_values=[genres], section_names=section_names)

