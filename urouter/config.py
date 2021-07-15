from ulogger import INFO
from . import logger

class _CONFIG:
    def __init__(self):
        self.charset = 'utf-8'
        self._buff_size = 1024
        self._logger_level = INFO
        self.request_timeout = 10
        self.max_connections = 5
    
    @property
    def buff_size(self):
        return self._buff_size
    
    @buff_size.setter
    def buff_size(self, value):
        from .router import response
        self._buff_size = value
        response._buf = bytearray(value)

    # =====================================

    @property
    def logger_level(self):
        return self._logger_level

    @logger_level.setter
    def logger_level(self, level):
        self.set_logger_level = level
        logger.handler.level = level



CONFIG = _CONFIG()