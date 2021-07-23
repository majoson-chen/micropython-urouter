from ulogger import INFO

class _CONFIG:
    def __init__(self):
        self.charset = 'utf-8'
        self._buff_size = 1024
        self._logger_level = INFO
        self.request_timeout = 7
        self.max_connections = 5
        self.debug = True
    

    def buff_size(self, app, value: int = None):
        """
        Set or get the buffer size of the response, the larger the value, the faster the processing speed.
        """
        if value:
            # set
            app.response._buf = bytearray(value)
        else:
            return len(app.response._buf)

    # =====================================

    @property
    def logger_level(self):
        return self._logger_level

    @logger_level.setter
    def logger_level(self, level):
        from .logger import handler
        self.set_logger_level = level
        handler.level = level



CONFIG = _CONFIG()