
from configparser import ConfigParser
from logging.handlers import TimedRotatingFileHandler
from typing import Literal, Union
import json
import logging
import os
import sys
import textwrap

from .__init__ import __version__
from .constants import *


def get_version():
    return __version__

class MalDiscLogging:
    def __init__(self):
        self.path = DIR_PATH + '/logs'
        self.filename = 'Script.log'
        self.full_path = os.path.join(self.path, self.filename)

        if not os.path.exists(self.path):
            os.mkdir(self.path)

    class _ColourFormatter(logging.Formatter):
        # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
        # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
        # The important ones here relate to colour.
        # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
        # 40-47 are the same except for the background
        # 90-97 are the same but "bright" foreground
        # 100-107 are the same as the bright ones but for the background.
        # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

        LEVEL_COLOURS = [
            (logging.DEBUG, '\x1b[40;1m'),
            (logging.INFO, '\x1b[34;1m'),
            (logging.WARNING, '\x1b[33;1m'),
            (logging.ERROR, '\x1b[31m'),
            (logging.CRITICAL, '\x1b[41m'),
        ]

        FORMATS = {
            level: logging.Formatter(
                f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s',
                '%Y-%m-%d %H:%M:%S',
            )
            for level, colour in LEVEL_COLOURS
        }

        def format(self, record):
            formatter = self.FORMATS.get(record.levelno)
            if formatter is None:
                formatter = self.FORMATS[logging.DEBUG]

            # Override the traceback to always print in red
            if record.exc_info:
                text = formatter.formatException(record.exc_info)
                record.exc_text = f'\x1b[31m{text}\x1b[0m'

            output = formatter.format(record)

            # Remove the cache layer
            record.exc_text = None
            return output

    def stream_supports_colour(self, stream) -> bool:
        is_a_tty = hasattr(stream, 'isatty') and stream.isatty()
        if sys.platform != 'win32':
            return is_a_tty

        # ANSICON checks for things like ConEmu
        # WT_SESSION checks if this is Windows Terminal
        # VSCode built-in terminal supports colour too
        return is_a_tty and ('ANSICON' in os.environ or 'WT_SESSION' in os.environ or os.environ.get('TERM_PROGRAM') == 'vscode')

    def setup_logging(
        self,
        *handler: logging.Handler,
        level: int = logging.DEBUG,
        ) -> logging.Logger:

        library, _, _ = __name__.partition('.')
        logger = logging.getLogger(f'maldisc.{library}')
        logger.setLevel(level)

        for hdlr in handler:
            if isinstance(hdlr, logging.StreamHandler) and self.stream_supports_colour(hdlr.stream):
                formatter = self._ColourFormatter()
            else:
                dt_fmt = '%Y-%m-%d %H:%M:%S'
                formatter = logging.Formatter(
                    '[{asctime}] [{levelname:<8}] {name}: {message}',
                    dt_fmt,
                    style = '{')

            hdlr.setFormatter(formatter)
            logger.addHandler(hdlr)

        return logger


    def stream_handler(self) -> logging.StreamHandler:
        handler = logging.StreamHandler()
        return handler

    def file_handler(self) -> logging.FileHandler:
        handler = TimedRotatingFileHandler(self.full_path, when='midnight', backupCount = 7)
        return handler

    def get_logger(self) -> logging.Logger:
        logger = self.setup_logging(
            *(self.stream_handler(),
            self.file_handler()))

        return logger

class MalDiscConfigParser:
    def __init__(self):
        self.config = ConfigParser()
        self.full_path = os.path.join(DIR_PATH, 'config.ini')

        if not os.path.exists(self.full_path):
            self.init_file()
            sys.exit(textwrap.dedent(
                f'''
                config.ini not found. A default one has been created under the following path:
                {DIR_PATH}/config.ini
                Please fill out the config.ini file before running the bot')
                '''))

        self.config.read(self.full_path)

    @property
    def sections(self) -> list:
        return self.config.sections()

    def init_file(self) -> None:
        self.config["BOT"] = {
            "Prefixes": [";", "-", "You may put as much prefix as you want"],
            "Token": "Get Your Bot Token here: https://discord.com/developers/applications"}

        self.config["FEATURES"] = {
            "EnableUrlDetection": True,
            "InteractionTimeout": 300.0}

        self.config["MAL_API"] = {
            "Enabled": False,
            "ClientID": "Get Your Client ID here: https://myanimelist.net/apiconfig"}

        with open(self.full_path, 'w+') as configfile:
            self.config.write(configfile)

    def read(self, datatype: Literal[str, list, int, float, bool],
             section: str, key: str) -> Union[str, list, int, float, bool]:

        if datatype == bool:
            return self.config.getboolean(section, key)
        elif datatype == list:
            return json.loads(self.config.get(section, key).replace("'", '"'))
        elif datatype == int:
            return self.config.getint(section, key)
        elif datatype == float:
            return self.config.getfloat(section, key)
        else:
            return self.config.get(section, key)
