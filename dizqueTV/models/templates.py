from typing import List

PLEX_SERVER_SETTINGS_TEMPLATE = {
    "name": str,
    "uri": str,
    "accessToken": str,
    "index": int,
    "arChannels": bool,
    "arGuide": bool,
    "_id": str
}

WATERMARK_SETTINGS_TEMPLATE = {
    "enabled": bool,
    "width": float,
    "verticalMargin": float,
    "horizontalMargin": float,
    "duration": int,
    "fixedSize": bool,
    "position": str,
    "url": str,
    "animated": bool
}

WATERMARK_SETTINGS_DEFAULT = {
    "enabled": False,
    "width": 6.25,
    "verticalMargin": 1.8518518518518519,
    "horizontalMargin": 1.0416666666666667,
    "duration": 60,
    "fixedSize": False,
    "position": "bottom-right",
    "url": "",
    "animated": False
}

CHANNEL_FFMPEG_SETTINGS_TEMPLATE = {
    "targetResolution": str,
    "videoBitrate": int,
    "videoBufSize": int
}

CHANNEL_FFMPEG_SETTINGS_DEFAULT = {
    "targetResolution": "",
    "videoBitrate": None,
    "videoBufSize": None
}

CHANNEL_ON_DEMAND_SETTINGS_TEMPLATE = {
    "isOnDemand": bool,
    "modulo": int,
    "paused": bool,
    "firstProgramModulo": int,
    "playedOffset": int,
}

CHANNEL_ON_DEMAND_SETTINGS_DEFAULT = {
    "isOnDemand": False,
    "modulo": 1,
    "paused": False,
    "firstProgramModulo": 1,
    "playedOffset": 0,
}

TIME_SLOT_SETTINGS_TEMPLATE = {
    "time": int,
    "showId": str,
    "order": str
}

SCHEDULE_SETTINGS_TEMPLATE = {
    "lateness": int,
    "maxDays": int,
    "flexPreference": ["end", "distribute"],
    "slots": [],
    "pad": int,
    "timeZoneOffset": int,
    "fake": dict
}

SCHEDULE_SETTINGS_DEFAULT = {
    "lateness": 0,
    "maxDays": 365,
    "flexPreference": "distribute",
    "slots": [],
    "pad": 1,
    "timeZoneOffset": 0,
    "fake": {
        "time": -1
    }
}

RANDOM_SCHEDULE_SETTINGS_TEMPLATE = {
    "lateness": int,
    "maxDays": int,
    "flexPreference": ["end", "distribute"],
    "slots": [],
    "pad": int,
    "padStyle": str,
    "randomDistribution": str,
    "timeZoneOffset": int,
    "fake": dict
}

RANDOM_SCHEDULE_SETTINGS_DEFAULT = {
    "lateness": 0,
    "maxDays": 365,
    "flexPreference": "distribute",
    "slots": [],
    "pad": 1,
    "padStyle": "slot",
    "randomDistribution": "uniform",
    "timeZoneOffset": 0,
    "fake": {
        "time": -1
    }
}

CHANNEL_SETTINGS_TEMPLATE = {
    "programs": List,
    "fillerRepeatCooldown": int,
    "fallback": [],
    "icon": str,
    "disableFillerOverlay": bool,
    "startTime": str,
    "offlinePicture": str,
    "offlineSoundtrack": str,
    "offlineMode": str,
    "number": int,
    "name": str,
    "duration": int,
    "_id": str,
    "fillerCollections": List,
    "watermark": {},
    "transcoding": {},
    "guideMinimumDurationSeconds": int,
    "guideFlexPlaceholder": str,
    "stealth": bool,
    "enabled": bool,
    "groupTitle": str
}

CHANNEL_SETTINGS_DEFAULT = {
    "fillerRepeatCooldown": 1800000,
    "fallback": [],
    "disableFillerOverlay": True,
    "offlineSoundtrack": "",
    "offlineMode": "pic",
    "fillerCollections": [],
    "watermark": WATERMARK_SETTINGS_DEFAULT,
    "transcoding": CHANNEL_FFMPEG_SETTINGS_DEFAULT,
    "guideMinimumDurationSeconds": 300,
    "guideFlexPlaceholder": "",
    "enabled": True,
    "stealth": False,
    "groupTitle": "dizqueTV"
}

FILLER_LIST_SETTINGS_TEMPLATE = {
    "name": str,
    "content": List,
    "id": str
}

FILLER_LIST_SETTINGS_DEFAULT = {
    "name": "New List",
    "content": []
}

FILLER_LIST_CHANNEL_TEMPLATE = {
    "id": str,
    "weight": int,
    "cooldown": int
}

FILLER_LIST_CHANNEL_DEFAULT = {
    "weight": 300,
    "cooldown": 0
}

REDIRECT_PROGRAM_TEMPLATE = {
    "isOffline": bool,
    "type": str,
    "duration": int,
    "channel": int
}

CUSTOM_SHOW_TEMPLATE = {
    "name": str,
    "content": List
}

MOVIE_PROGRAM_TEMPLATE = {
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

EPISODE_PROGRAM_TEMPLATE = {
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
    "serverKey": str,
    "showIcon": str,
    "episodeIcon": str,
    "seasonIcon": str
}

TRACK_PROGRAM_TEMPLATE = {
    "title": str,
    "key": str,
    "ratingKey": str,
    "icon": str,
    "type": str,
    "summary": str,
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

IMAGE_UPLOAD_RESPONSE_TEMPLATE = {
    "name": str,
    "mimetype": str,
    "size": int,
    "fileUrl": str
}
