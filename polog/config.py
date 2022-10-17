from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.stores.levels import Levels
from polog.core.utils.signature_matcher import SignatureMatcher
from polog.core.utils.pony_names_generator import PonyNamesGenerator
from polog.core.utils.name_manager import NameManager
from polog.core.stores.handlers import global_handlers
from polog.data_structures.trees.named_tree.projector import TreeProjector
from polog.core.stores.fields import in_place_fields, engine_fields
from polog.loggers.auto.function_logger import flog
from polog.loggers.handle.handle_log import handle_log
from polog.loggers.handle.message import message
from polog import log


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
        Запрещено использовать имена, которые пересекаются с именами, используемыми в качестве имен методов в логгерах. Это необходимо, поскольку имена логирования можно использовать в качестве динамических методов логгеров, и нужно, чтобы они не пересекались.
        """
        forbidden_names = set(dir(flog)).union(set(dir(handle_log))).union(set(dir(log))).union(set(dir(message)))
        for key, value in kwargs.items():
            if not isinstance(value, int):
                raise TypeError(f'Variable "{key}" has not type int.')
            if value < 0:
                raise ValueError('The logging level cannot be less than zero.')
            estimate_of_name = NameManager.is_possible_level_name(key)
            if not estimate_of_name.possibility:
                raise NameError(estimate_of_name.reason)
            Levels.set(key, value)

    @staticmethod
    def standard_levels():
        """
        Установка уровней логирования в соответствии со стандартной схемой.
        См. https://docs.python.org/3.8/library/logging.html#logging-levels
        """
        levels = {'NOTSET': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
        for key, value in levels.items():
            Levels.set(key, value)
            Levels.set(key.lower(), value)

    @classmethod
    def add_handlers(cls, *args, **kwargs):
        """
        Добавляем обработчики для логов.
        Сюда можно передать несколько обработчиков через запятую. Если их передавать как именованные переменные, они будут сохранены под соответствующими именами. Если как неименованные - имена будут сгенерированы автоматически.
        Также сюда можно передавать словари в качестве неименованных параметров. Ключи должны быть именами обработчиков (вернее, путями к ним), а значения - самими обработчиками.

        Каждый обработчик должен быть вызываеым объектом, имеющим следующую сигнатуру (названия параметров соблюдать не обязательно):

        >>> def handler(log_item):
        >>> ... pass

        При несовпадении сигнатуры, будет поднято исключение.

        Один и тот же объект обработчика нельзя зарегистрировать дважды. Также нельзя использовать для двух обработчиков одно имя. В обоих случаях будет поднято исключение.
        """
        for handler in args:
            if isinstance(handler, dict):
                for name, value in handler.items():
                    if not isinstance(name, str):
                        raise KeyError('Only strings can be used as the handler name.')
                    cls.set_handler(name, value)
            else:
                if id(handler) in {id(node.value) for node in global_handlers.childs.values()}:
                    raise ValueError('An attempt to store the same handler object in a global namespace.')
                handler_name = next(cls.pony_names_generator).replace(' ', '_')
                cls.set_handler(handler_name, handler)
        for handler_name, handler in kwargs.items():
            cls.set_handler(handler_name, handler)

    @classmethod
    def set_handler(cls, name, handler):
        """
        Сохраняем обработчик под каким-то именем.
        """
        if name in global_handlers:
            raise NameError(f'Attempt to override a handler named {name}.')
        global_handlers[name] = handler

    @staticmethod
    def get_handlers(*names):
        """
        Получаем словаре-подобный объект, где ключи - имена обработчиков, а значения - сами зарегистрированные в Polog обработчики.

        Если метод вызвать без аргументов, будет возвращен полный набор зарегистрированных обработчиков.
        В качестве аргументов можно передать имена нужных обработчиков, тогда в полученном словаре будут только они.
        Если ранее не был зарегистрирован обработчик с указанным именем, в возвращаемом словаре вместо него будет None.
        """
        if not names:
            return global_handlers

        projector = TreeProjector(global_handlers)
        local_scope_tree = projector.on(names)
        return local_scope_tree

    @staticmethod
    def delete_handlers(*names):
        """
        Удаление ранее зарегистрированного обработчика.

        Сюда можно передать как имя обработчика, так и сам обработчик.
        Если обработчик будет найден по имени или по id, он будет удален. В противном случае - поднимется исключение.
        Возможно удаление нескольких обработчиков, перечисленных через запятую.
        """
        for maybe_name in names:
            if isinstance(maybe_name, str):
                del global_handlers[maybe_name]
            else:
                handler = maybe_name
                other_handlers = {id(node.value): node.name for node in global_handlers.childs.values()}
                if id(handler) not in other_handlers:
                    raise ValueError(f'Object "{handler}" was not found among the global name scope handlers.')
                handler_name = other_handlers[id(handler)]
                del global_handlers[handler_name]

    @staticmethod
    def add_fields(**fields):
        """
        Добавляем кастомные "поля" логов.

        Данные поля будут извлекаться в том же потоке, в котором собственно происходит логируемое событие. За счет этого возможно залогировать, к примеру, идентификатор потока, в котором произошло событие.

        Поле - это некоторый объект, имеющий метод .get_data() с той же сигнатурой, что у обработчиков (см. комментарий к методу .add_handlers() этого же класса). Он будет вызываться при каждом формировании лога, а результат его работы - передаваться обработчикам так же, как и все прочие поля.

        В данном случае поля передаются в виде именованных переменных, где имена переменных - это названия полей, а значения - сами функции.
        """
        for key, value in fields.items():
            if not hasattr(value, 'get_data') or not SignatureMatcher.is_handler(value.get_data):
                raise ValueError('The field handler must have a method .get_data() with the signature that is standard for Polog handlers.')
            estimate_of_name = NameManager.is_possible_extra_field_name(key)
            if not estimate_of_name.possibility:
                raise NameError(estimate_of_name.reason)
            in_place_fields[key] = value

    @staticmethod
    def add_engine_fields(**fields):
        """
        Добавляем кастомные "поля" логов, которые будут извлекаться внутри движка. В остальном идентично тем полям, что добавляются через .add_fields().
        """
        for key, value in fields.items():
            if not hasattr(value, 'get_data') or not SignatureMatcher.is_handler(value.get_data):
                raise ValueError('The field handler must have a method .get_data() with the signature that is standard for Polog handlers.')
            estimate_of_name = NameManager.is_possible_extra_field_name(key)
            if not estimate_of_name.possibility:
                raise NameError(estimate_of_name.reason)
            engine_fields[key] = value

    @staticmethod
    def delete_fields(*fields):
        """
        Удаляем кастомные поля по их названиям. См. метод .add_fields().
        """
        settings = SettingsStore()
        for name in fields:
            if not isinstance(name, str):
                raise KeyError('Fields are deleted by name. The name is an instance of the str class.')
            in_place_fields.pop(name)

    @staticmethod
    def delete_engine_fields(*fields):
        """
        Удаляем кастомные поля по их названиям. См. метод .add_engine_fields().
        """
        settings = SettingsStore()
        for name in fields:
            if not isinstance(name, str):
                raise KeyError('Fields are deleted by name. The name is an instance of the str class.')
            engine_fields.pop(name)

    @staticmethod
    def get_in_place_fields(*names):
        """
        Получаем словарь с извлекаемыми "на месте" полями.
        Если сюда передать одно или несколько имен полей, вернется словарь только с ними, иначе - со всеми.
        """
        if not names:
            return {**in_place_fields}
        return {name: in_place_fields.get(name) for name in names if in_place_fields.get(name) is not None}

    @staticmethod
    def get_engine_fields(*names):
        """
        Получаем словарь с извлекаемыми внутри движка полями.
        Если сюда передать одно или несколько имен полей, вернется словарь только с ними, иначе - со всеми.
        """
        if not names:
            return {**engine_fields}
        return {name: engine_fields.get(name) for name in names if engine_fields.get(name) is not None}

    @classmethod
    def get_all_fields(cls, *names):
        """
        Метод возвращает вообще все ивлекаемые поля, то есть извлекаемые как внутри движка, так и "на месте".
        В случае пересечения имен, результат будет идентичен порядку реального извлечения полей, то есть движковые поля "затрут" конкурентов.
        """
        result = {**cls.get_in_place_fields(*names)}
        result.update(cls.get_engine_fields(*names))
        return result
