import logging

from warnings import warn


class ColorFormatter(logging.Formatter):

    def __init__(self, _logging=None, colorizer=None, *a, **kw):
        logging.Formatter.__init__(self, *a, **kw)
        warn(
            'pecan.log.ColorFormatter is no longer supported; consider an alternative library such as https://pypi.org/project/colorlog/',
            DeprecationWarning
        )

    def format(self, record):
        record.color_levelname = ''
        record.padded_color_levelname = record.levelname
        return logging.Formatter.format(self, record)
