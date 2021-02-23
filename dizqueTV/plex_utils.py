from typing import List, Union

from plexapi import server, media, library, playlist, myplex


class PlexUtils:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.server = server.PlexServer(url, token)

    @property
    def users(self) -> List[myplex.MyPlexUser]:
        return self.server.myPlexAccount().users()

    @property
    def playlists(self) -> List[playlist.Playlist]:
        return self.server.playlists()

    @property
    def library_sections(self) -> List[library.LibrarySection]:
        return self.server.library.sections()

    def user_has_server_access(self, user: myplex.MyPlexUser) -> bool:
        for s in user.servers:
            if s.name == self.server.friendlyName:
                return True
        return False

    def get_playlist(self, playlist_name: str) -> Union[playlist.Playlist, None]:
        for playlist in self.playlists:
            if playlist.title == playlist_name:
                return playlist
        return None

    def create_new_playlist(self, playlist_name: str, items: List[media.Media]) -> bool:
        try:
            self.server.createPlaylist(title=playlist_name, items=items)
            return True
        except:
            return False

    def reset_playlist(self, playlist_name: str, items: List[media.Media]) -> bool:
        try:
            playlist = self.get_playlist(playlist_name=playlist_name)
            if playlist:
                playlist.delete()
            self.create_new_playlist(playlist_name=playlist_name, items=items)
            return True
        except:
            return False

    def get_all_section_items(self, section: library.LibrarySection) -> List[media.Media]:
        return section.all()

    def search_for_plex_items(self, section_name: str = None, result_class = None, **search_terms) -> List[media.Media]:
        if section_name:
            results = self.server.library.section(section_name).search(**search_terms)
        else:
            results = self.server.library.search(**search_terms)
        if result_class:
            return [item for item in results if isinstance(item, result_class)]
        return results

    def get_dizque_item_on_plex(self, dizque_item, section_name: str = None) -> Union[media.Media, None]:
        if section_name:
            results = self.server.library.section(section_name).search(title=dizque_item.title)
        else:
            results = self.server.library.search(title=dizque_item.title)
        for plex_item in results:
            if plex_item.ratingKey and int(plex_item.ratingKey) == int(dizque_item.ratingKey):
                return plex_item
        return None

