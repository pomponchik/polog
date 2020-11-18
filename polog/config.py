from polog.base_settings import BaseSettings
from polog.levels import Levels


class config:
    """
    Установка глобальных параметров логгера.
    """
    allowed_settings = {
        'pool_size': (int, ),
        'service_name': (str, ),
        'level': (int, str),
        'errors_level': (int, str),
        'original_exceptions': (bool, ),
        'delay_before_exit': (float, int, ),
    }
    convert_values = {
        'level': Levels.get,
        'errors_level': Levels.get,
    }

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

    @staticmethod
    def add_handlers(*args):
        """
        Добавляем обработчики для логов. Сюда можно передать несколько обработчиков через запятую.
        """
        settings = BaseSettings()
        for handler in args:
            if not callable(handler):
                raise ValueError(f'Object od type "{handler.__class__.__name__}" can not be a handler.')
            settings.handlers.append(handler)
