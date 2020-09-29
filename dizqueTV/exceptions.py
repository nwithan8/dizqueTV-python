class MissingSettingsError(Exception):
    def __init__(self, message):
        super().__init__(f"The provided settings are incomplete. {message}")


class MissingParametersError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NotRemoteObjectError(Exception):
    def __init__(self, object_type: str):
        super().__init__(f"Local {object_type} object does not exist on dizqueTV.")


class ItemCreationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ChannelCreationError(Exception):
    def __init__(self, message):
        super().__init__(message)
