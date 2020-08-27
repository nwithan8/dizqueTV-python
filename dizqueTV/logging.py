import logging

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.INFO)


def info(message):
    logging.info(msg=message)


def error(message):
    logging.error(msg=message)


def warning(message):
    logging.warning(msg=message)
