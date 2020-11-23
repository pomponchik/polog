from threading import Lock


class BaseSettings:
    pool_size = 2
    original_exceptions = False
    level = 1
    service_name = 'base'
    errors_level = 2
    delay_before_exit = 1.0
    handlers = []

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.__class__, key, value)

    def __new__(cls, **kwargs):
        with Lock():
            if not hasattr(cls, 'instance'):
                cls.instance = super(BaseSettings, cls).__new__(cls)
            return cls.instance
