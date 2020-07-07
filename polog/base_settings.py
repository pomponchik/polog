class BaseSettings(object):
    pool_size = 1
    original_exceptions = False
    level = 1
    service_name = 'base'
    errors_level = 2

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.__class__, key, value)

    def __new__(cls, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(BaseSettings, cls).__new__(cls)
        return cls.instance
