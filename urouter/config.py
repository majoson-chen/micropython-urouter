from ulogger import INFO
from . import logger


class _CONFIG:
    def __init__(self):
        self.charset = 'utf-8'
        self.keep_alive = False
        self.buff_size = 1024
        self._logger_level = INFO
        self.request_timeout = 10
    
    @property
    def logger_level(self):
        return self._logger_level

    @logger_level.setter
    def logger_level(self, level):
        self.set_logger_level = level
        logger.handler.level = level



CONFIG = _CONFIG()