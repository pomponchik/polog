from polog.core.base_settings import BaseSettings
from polog.core.levels import Levels
from polog.core.utils.is_handler import is_handler


class config:
    """
    Установка глобальных параметров логгера.

    Все методы тут статические, что позволяет вызывать их просто через точку, например:
    config.set(pool_size=5)
    """
    # Разрешенные настройки и соответствующие им типы данных.
    # Через метод .set() невозможно установить настройку с иным названием или неподходящим типом данных, поднимется KeyError.
    allowed_settings = {
        'pool_size': (int, ),
        'service_name': (str, ),
        'level': (int, str),
        'errors_level': (int, str),
        'original_exceptions': (bool, ),
        'delay_before_exit': (float, int, ),
    }
    # Функции, которые применяются к пользовательскому вводу настроек перед тем, как их сохранить.
    convert_values = {
        'level': Levels.get,
        'errors_level': Levels.get,
    }

    @staticmethod
    def set(**kwargs):
        """
        Установка глобальных параметров логирования.

        Новые параметры передаются в виде именованных аргументов. Разрешенные названия аргументов - ключи в self.allowed_settings. Разрешенные типы перечислены в кортежах, которые являются значениями в self.allowed_settings.
        При попытке установить настройку не разрешенного типа - поднимется KeyError.

        Настройки фактически сохраняются в классе BaseSettings. В настоящий момент возможность защита от конкурентной записи настроек НЕ гарантируется.

        Важно: Polog гарантирует применение настроек только в том случае, если они были установлены ДО момента первой записи лога.
        Рекомендуется устанавливать все настройки во входном файле программы, до того, как начнет исполняться основной код.
        """
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
            if value < 0:
                raise ValueError('The logging level cannot be less than zero.')
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

        Каждый обработчик должен быть вызываеым объектом, имеющим следующую сигнатуру (названия параметров соблюдать не обязательно):

        handler(function_input, **fields)

        При несовпадении сигнатуры, будет поднято исключение.

        Если ранее тот же обработчик уже был добавлен, он не дублируется.
        """
        settings = BaseSettings()
        old_handlers_ids = {id(x) for x in settings.handlers}
        for handler in args:
            if not callable(handler):
                raise ValueError(f'Object od type "{handler.__class__.__name__}" can not be a handler.')
            if not is_handler(handler):
                raise ValueError('This object cannot be a Polog handler, because the signatures do not match.')
            if id(handler) not in old_handlers_ids:
                settings.handlers.append(handler)

    @staticmethod
    def add_fields(**fields):
        """
        Добавляем кастомные "поля" логов.

        Поле - это некоторый объект, имеющий метод .get_data() с той же сигнатурой, что у обработчиков (см. комментарий к методу .add_handlers() этого же класса). Он будет вызываться при каждом формировании лога, а результат его работы - передаваться обработчикам так же, как и все прочие поля.

        В данном случае поля передаются в виде именованных переменных, где имена переменных - это названия полей, а значения - сами функции.
        """
        settings = BaseSettings()
        for key, value in fields.items():
            if not hasattr(value, 'get_data') or not is_handler(value.get_data):
                raise ValueError('The signature of the field handler must be the same as that of other Polog handlers.')
            settings.extra_fields[key] = value
