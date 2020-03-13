import logging
import sys
import os


def _formatter():
    return logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")


def _console_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_formatter())
    return handler


def _file_handler(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    file_handler = logging.FileHandler(os.path.join(path, "everviz.log"))
    file_handler.setFormatter(_formatter())
    return file_handler


def setup_logger(path):
    logger = logging.getLogger("everviz")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_console_handler())
    logger.addHandler(_file_handler(path))
    logger.propagate = False
    return logger


def get_logger():
    return logging.getLogger("everviz")
