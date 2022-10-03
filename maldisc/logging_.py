
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from colorama import Back, Fore, Style

from .constants import *

FORMATTER = logging.Formatter(
    f'[%(asctime)s][%(levelname)s][%(name)s]	%(message)s')
CONSOLE_FORMATTER = logging.Formatter(
    f'{Fore.BLACK + Style.BRIGHT}%(asctime)s {Fore.BLUE}%(levelname)s     {Style.RESET_ALL + Fore.LIGHTMAGENTA_EX + Style.DIM}%(name)s {Style.RESET_ALL}%(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S')

FILE_PATH = DIR_PATH + '/logs'
FILE_NAME = 'Script.log'
LOG_FILE = os.path.join(FILE_PATH, FILE_NAME)

if not os.path.exists(FILE_PATH):
    os.mkdir(FILE_PATH + '/logs')

def _get_console_handler():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CONSOLE_FORMATTER)
    return console_handler

def _get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount = 7)
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG) # Better to have too much log than not enough
    logger.addHandler(_get_console_handler())
    logger.addHandler(_get_file_handler())
    # With this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger

def remove_handler(logger):
    for h in range(len(logger.handlers)): logger.removeHandler(logger.handlers[0])
    return logger

def shutdown():
    logging.shutdown()
    return True
