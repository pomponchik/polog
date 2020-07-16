from polog.errors import DatabaseIsAlreadyDeterminedError
from polog.connector import Connector
from polog.base_settings import BaseSettings
from polog.levels import Levels


class Config(object):
    """
    Установка глобальных параметров логгера. Тут можно настроить, в какую базу данных будут писаться логи, и много других вещей.
    """
    allowed_settings = {
        'pool_size': int,
        'service_name': str,
        'level': int,
        'errors_level': int,
        'original_exceptions': bool,
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
    def settings(**kwargs):
        for key, value in kwargs.items():
            if key not in Config.allowed_settings.keys():
                raise ValueError(f'"{key}" variable is not allowed for the log settings.')
            allowed_type = Config.allowed_settings.get(key)
            if not isinstance(value, allowed_type):
                raise TypeError(f'Variable "{key}" has not type {allowed_type.__name__}.')
        BaseSettings(**kwargs)

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
