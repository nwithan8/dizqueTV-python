from functools import wraps

from dizqueTV.exceptions import NotRemoteObjectError


def check_for_dizque_instance(func: object):
    """
    Check if an object has a _dizque_instance attribute before executing function

    :param func: Function to execute if object does have a _dizque_instance attribute
    :type func: object
    :return: Result of func
    :rtype: object
    """

    @wraps(func)
    def inner(obj, **kwargs):
        if obj._dizque_instance:
            return func(obj, **kwargs)
        raise NotRemoteObjectError(object_type=type(obj).__name__)
    return inner