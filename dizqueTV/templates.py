from typing import List

PLEX_SETTINGS_TEMPLATE = {
    "name": str,
    "uri": str,
    "accessToken": str,
    "index": int,
    "arChannels": bool,
    "arGuide": bool,
    "_id": str
}

CHANNEL_SETTINGS_TEMPLATE = {
    "programs": List,
    "fillerContent": List,
    "fillerRepeatCooldown": int,
    "fallback": [],
    "icon": str,
    "disableFillerOverlay": bool,
    "iconWidth": int,
    "iconDuration": int,
    "iconPosition": str,
    "startTime": str,
    "offlinePicture": str,
    "offlineSoundtrack": str,
    "offlineMode": str,
    "number": int,
    "name": str,
    "duration": int,
    "_id": str,
    "overlayIcon": bool
}

PROGRAM_ITEM_TEMPLATE = {
    "title": str,
    "key": str,
    "ratingKey": str,
    "icon": str,
    "type": str,
    "duration": int,
    "summary": str,
    "rating": str,
    "date": str,
    "year": int,
    "plexFile": str,
    "file": str,
    "showTitle": str,
    "episode": int,
    "season": int,
    "serverKey": str
}

FILLER_ITEM_TEMPLATE = {
    "title": str,
    "key": str,
    "ratingKey": str,
    "icon": str,
    "type": str,
    "duration": int,
    "summary": str,
    "date": str,
    "year": int,
    "plexFile": str,
    "file": str,
    "showTitle": str,
    "episode": int,
    "season": int,
    "serverKey": str
}