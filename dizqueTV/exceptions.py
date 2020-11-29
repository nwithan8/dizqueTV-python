import inspect

@property
def _errored_func():
    return inspect.trace()[-1].function


class IncludeFunctionName(Exception):
    def __init__(self, message):
        super().__init__(f"Error in '{_errored_func()}' function\n{message}")


class GeneralException(IncludeFunctionName):
    def __init__(self, message):
        super().__init__(message)


class MissingSettingsError(IncludeFunctionName):
    def __init__(self, message):
        super().__init__(f"The provided settings are incomplete. {message}")


class MissingParametersError(IncludeFunctionName):
    def __init__(self, message):
        super().__init__(message)


class NotRemoteObjectError(IncludeFunctionName):
    def __init__(self, object_type: str):
        super().__init__(f"Local {object_type} object does not exist on dizqueTV.")


class ItemCreationError(IncludeFunctionName):
    def __init__(self, message):
        super().__init__(message)


class ChannelCreationError(IncludeFunctionName):
    def __init__(self, message):
        super().__init__(message)
