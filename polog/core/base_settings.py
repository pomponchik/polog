from threading import Lock
from polog.utils.read_only_singleton import ReadOnlySingleton


class BaseSettings(ReadOnlySingleton):
    pool_size = 2
    original_exceptions = False
    level = 1
    service_name = 'base'
    errors_level = 2
    delay_before_exit = 1.0
    handlers = []
    extra_fields = {}

    def __init__(self, **kwargs):
        with Lock():
            for key, value in kwargs.items():
                setattr(self.__class__, key, value)
