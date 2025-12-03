import inspect
import platform

from dizqueTV._info import __version__ as version


@property
def _errored_func():
    return inspect.trace()[-1].function


def _platform_info(dtv_api):
    return f"os:{platform.system()}|pyv:{platform.python_version()}|libv:{version}|softv:{dtv_api.dizquetv_version}"


class IncludeFunctionName(Exception):
    def __init__(self, message: str, errored_function: str = None):
        if not errored_function:
            errored_function = _errored_func
        super().__init__(f"Error in '{errored_function}' function\n{message}")


class ReportedException(IncludeFunctionName):
    def __init__(
        self,
        message: str,
    ):
        errored_function = str(_errored_func)
        super().__init__(message, errored_function=errored_function)


class GeneralException(IncludeFunctionName):
    def __init__(self, message: str):
        super().__init__(message)


class MissingSettingsError(IncludeFunctionName):
    def __init__(self, message: str):
        super().__init__(f"The provided settings are incomplete. {message}")


class MissingParametersError(IncludeFunctionName):
    def __init__(self, message: str):
        super().__init__(message)


class NotRemoteObjectError(IncludeFunctionName):
    def __init__(self, object_type: str):
        super().__init__(f"Local {object_type} object does not exist on dizqueTV.")


class ItemCreationError(IncludeFunctionName):
    def __init__(self, message: str):
        super().__init__(message)


class ChannelCreationError(IncludeFunctionName):
    def __init__(self, message: str):
        super().__init__(message)
