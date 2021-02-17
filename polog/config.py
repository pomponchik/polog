from polog.core.base_settings import BaseSettings
from polog.core.levels import Levels


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
                raise KeyError(f'"{key}" variable is not allowed for the log settings.')
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
        Если ранее тот же обработчик уже был добавлен, он не дублируется.
        """
        settings = BaseSettings()
        old_handlers_ids = [id(x) for x in settings.handlers]
        for handler in args:
            if not callable(handler):
                raise ValueError(f'Object od type "{handler.__class__.__name__}" can not be a handler.')
            if id(handler) not in old_handlers_ids:
                settings.handlers.append(handler)

    @staticmethod
    def add_fields(**fields):
        """
        Добавляем кастомные "поля" логов.
        Поле - это некоторая функция, имеющая ту же сигнатуру, что и обработчики. Она будет вызываться при каждом формировании лога, а результат ее работы - передаваться обработчикам так же, как и все прочие поля.

        В данном случае поля передаются в виде именованных переменных, где имена переменных - это названия полей, а значения - сами функции.
        """
        settings = BaseSettings()
        for key, value in fields.items():
            settings.extra_fields[key] = value
