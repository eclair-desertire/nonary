import logging


def save_info(message):
    db_logger = logging.getLogger('db')
    db_logger.info(message)


def save_warning(message):
    db_logger = logging.getLogger('db')
    db_logger.warning(message)


def save_exception(e):
    db_logger = logging.getLogger('db')
    db_logger.exception(e)
