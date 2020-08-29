class MissingSettingsError(Exception):
    def __init__(self):
        super().__init__("The provided settings are incomplete.")


class MissingParametersError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NotRemoteObjectError(Exception):
    def __init__(self, object_type: str):
        super().__init__(f"Local {object_type} object does not exist on dizqueTV.")
