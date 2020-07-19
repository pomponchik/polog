from polog.errors import DatabaseIsAlreadyDeterminedError
from polog.connector import Connector
from polog.base_settings import BaseSettings
from polog.levels import Levels


class config(object):
    """
    Установка глобальных параметров логгера. Тут можно настроить, в какую базу данных будут писаться логи, и много других вещей.
    """
    allowed_settings = {
        'pool_size': (int, ),
        'service_name': (str, ),
        'level': (int, str),
        'errors_level': (int, str),
        'original_exceptions': (bool, ),
    }
    convert_values = {
        'level': Levels.get,
        'errors_level': Levels.get,
    }

    @classmethod
    def db(cls, **kwargs):
        """
        Логгер Polog использует Pony ORM. В данный метод передаются аргументы так же, как в метод db.bind() самой Pony.
        См.: https://docs.ponyorm.org/database.html

        Скажем, базу данных sqlite можно инициализировать, вызвав данный метод как-то так:
        Config.db(provider='sqlite', filename=os.path.join(os.getcwd(), 'logs.db'), create_db=True)
        (именно так это и будет сделано по умолчанию, если этот метод  не будет вызван.)
        """
        if hasattr(cls, 'db_determined'):
            raise DatabaseIsAlreadyDeterminedError('You have already defined a database for logging. Forgot?')
        connect = Connector(**kwargs)
        setattr(cls, 'db_determined', True)

    @staticmethod
    def set(**kwargs):
        new_kwargs = {}
        for key, value in kwargs.items():
            if key not in config.allowed_settings.keys():
                raise ValueError(f'"{key}" variable is not allowed for the log settings.')
            allowed_types = config.allowed_settings.get(key)
            is_allowed = False
            for one in allowed_types:
                if isinstance(value, one):
                    is_allowed = True
            if not is_allowed:
                allowed_types = ', '.join(allowed_types)
                raise TypeError(f'Variable "{key}" has not one of types: {allowed_types}.')
            if key in config.convert_values:
                handler = config.convert_values[key]
                value = handler(value)
            new_kwargs[key] = value
        BaseSettings(**new_kwargs)

    @staticmethod
    def levels(**kwargs):
        """
        Установка кастомных уровней логирования.
        Имена переменных здесь соответствуют названиям новых уровней логирования, а их значения - собственно сами уровни.
        """
        for key, value in kwargs.items():
            if not isinstance(value, int):
                raise TypeError(f'Variable "{key}" has not type int.')
            Levels.set(key, value)

    @staticmethod
    def standart_levels():
        """
        Установка уровней логирования в соответствии со стандартной схемой:
        https://docs.python.org/3.8/library/logging.html#logging-levels
        """
        levels = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
        for key, value in levels.items():
            Levels.set(key, value)
