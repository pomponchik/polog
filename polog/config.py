from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.stores.levels import Levels
from polog.core.utils.signature_matcher import SignatureMatcher
from polog.core.utils.pony_names_generator import PonyNamesGenerator
from polog.core.stores.handlers import global_handlers


class config:
    """
    Установка глобальных параметров логгера.

    Все методы тут статические, что позволяет вызывать их просто через точку, например:
    config.set(pool_size=5)
    """
    # Генератор имен для обработчиков.
    pony_names_generator = PonyNamesGenerator().get_next_pony()

    @staticmethod
    def set(**kwargs):
        """
        Установка глобальных параметров логирования.

        Новые параметры передаются в виде именованных аргументов. Разрешенные названия аргументов - ключи в self.allowed_settings. Разрешенные типы перечислены в кортежах, которые являются значениями в self.allowed_settings.
        При попытке установить настройку не разрешенного типа - поднимется KeyError.

        Настройки фактически сохраняются в классе SettingsStore. В настоящий момент возможность защита от конкурентной записи настроек НЕ гарантируется.

        Важно: Polog гарантирует применение настроек только в том случае, если они были установлены ДО момента первой записи лога.
        Рекомендуется устанавливать все настройки во входном файле программы, до того, как начнет исполняться основной код.
        """
        for key, value in kwargs.items():
            SettingsStore()[key] = value

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
        Установка уровней логирования в соответствии со стандартной схемой (кроме уровня NOTSET):
        https://docs.python.org/3.8/library/logging.html#logging-levels
        """
        levels = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
        for key, value in levels.items():
            Levels.set(key, value)

    @classmethod
    def add_handlers(cls, *args, **kwargs):
        """
        Добавляем обработчики для логов.
        Сюда можно передать несколько обработчиков через запятую. Если их передавать как именованные переменные, они будут сохранены под соответствующими именами. Если как неименованные - имена будут сгенерированы автоматически.

        Каждый обработчик должен быть вызываеым объектом, имеющим следующую сигнатуру (названия параметров соблюдать не обязательно):

        handler(function_input, **fields)

        При несовпадении сигнатуры, будет поднято исключение.

        Один и тот же объект обработчика нельзя зарегистрировать дважды. Также нельзя использовать для двух обработчиков одно имя. В обоих случаях будет поднято исключение.
        """
        for handler in args:
            handler_name = next(cls.pony_names_generator).replace(' ', '_')
            cls.set_handler(handler_name, handler)
        for handler_name, handler in kwargs.items():
            cls.set_handler(handler_name, handler)

    @classmethod
    def set_handler(cls, name, handler):
        """
        Сохраняем обработчик под каким-то именем.
        """
        settings = SettingsStore()
        #old_handlers_ids = {id(x) for x in global_handlers}
        #old_ids_and_names = {id(y): x for x, y in settings.handlers.items()}
        #old_handlers_names = {x for x in settings.handlers.keys()}
        #if name in old_handlers_names:
        #    raise KeyError(f'A handler named "{name}" is already registered.')
        #if id(handler) in old_handlers_ids:
        #    name = [x for x, y in settings.handlers.items() if id(y) == id(handler)][0]
        #    raise ValueError(f'Handler {handler} is already registered under the name "{name}".')
        global_handlers[name] = handler

    @staticmethod
    def get_handlers(*names):
        """
        Получаем словарь, где ключи - имена обработчиков, а значения - сами зарегистрированные в Polog обработчики.

        Если метод вызвать без аргументов, будет возвращен полный набор зарегистрированных обработчиков.
        В качестве аргументов можно передать имена нужных обработчиков, тогда в полученном словаре будут только они.
        Если ранее не был зарегистрирован обработчик с указанным именем, в возвращаемом словаре вместо него будет None.
        """
        if not names:
            return {**(global_handlers)}
        result = {}
        for name in names:
            if not isinstance(name, str):
                raise KeyError('The handler name must be a string.')
            handler = SettingsStore().handlers.get(name)
            result[name] = handler
        return result

    @staticmethod
    def delete_handlers(*names):
        """
        Удаление ранее зарегистрированного обработчика. Сюда можно передать как имя обработчика, так и сам обработчик.
        Если обработчик будет найден по имени или по id, он будет удален. В противном случае - поднимется исключение.
        Возможно удаление нескольких обработчиков, перечисленных через запятую.
        """
        ids_to_names = {id(handler): name for name, handler in SettingsStore().handlers.items()}
        for maybe_name in names:
            if isinstance(maybe_name, str):
                try:
                    SettingsStore().handlers.pop(maybe_name)
                except KeyError:
                    raise KeyError(f'Object {maybe_name} was not registered as a handler.')
            else:
                object_id = id(maybe_name)
                if object_id in ids_to_names:
                    handler_name = ids_to_names[object_id]
                    SettingsStore().handlers.pop(handler_name)
                else:
                    raise ValueError(f'Object {maybe_name} was not registered as a handler.')

    @staticmethod
    def add_fields(**fields):
        """
        Добавляем кастомные "поля" логов.

        Поле - это некоторый объект, имеющий метод .get_data() с той же сигнатурой, что у обработчиков (см. комментарий к методу .add_handlers() этого же класса). Он будет вызываться при каждом формировании лога, а результат его работы - передаваться обработчикам так же, как и все прочие поля.

        В данном случае поля передаются в виде именованных переменных, где имена переменных - это названия полей, а значения - сами функции.
        """
        settings = SettingsStore()
        for key, value in fields.items():
            if not hasattr(value, 'get_data') or not SignatureMatcher.is_handler(value.get_data):
                raise ValueError('The signature of the field handler must be the same as that of other Polog handlers.')
            settings.extra_fields[key] = value

    @staticmethod
    def delete_fields(*fields):
        """
        Удаляем кастомные поля по их названиям. См. метод .add_fields().
        """
        settings = SettingsStore()
        for name in fields:
            if not isinstance(name, str):
                raise KeyError('Fields are deleted by name. The name is an instance of the str class.')
            settings.extra_fields.pop(name)
