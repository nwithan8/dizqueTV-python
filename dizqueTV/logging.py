import logging


def info(message):
    logging.info(msg=message)


def error(message):
    logging.error(msg=message)


def warning(message):
    logging.warning(msg=message)


level_map = {
    'info': info,
    'error': error,
    'warning': warning
}


def log(message: str, level: str = "info") -> None:
    """
    Log a message if verbose is enabled.

    :param message: Message to log
    :param level: info, error or warning
    :return: None
    :rtype: None
    """
    if level not in level_map.keys():
        level = 'info'
    level_map[level](message)
