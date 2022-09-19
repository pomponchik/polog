import time
import inspect
import datetime
from functools import wraps
from collections.abc import Iterable

from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.stores.handlers import global_handlers
from polog.core.engine.engine import Engine
from polog.core.stores.levels import Levels
from polog.core.stores.registering_functions import RegisteringFunctions
from polog.core.utils.not_none_to_dict import not_none_to_dict
from polog.core.utils.get_errors_level import get_errors_level
from polog.core.utils.exception_to_dict import exception_to_dict
from polog.utils.json_vars import json_vars, json_one_variable
from polog.core.utils.signature_matcher import SignatureMatcher
from polog.core.utils.get_traceback import get_traceback, get_locals_from_traceback
from polog.errors import IncorrectUseOfTheDecoratorError, HandlerNotFoundError
from polog.loggers.handle.message import message as _message
from polog.core.log_item import LogItem
from polog.data_structures.trees.named_tree.projector import TreeProjector
from polog.core.utils.pony_names_generator import PonyNamesGenerator
from polog.core.stores.fields import in_place_fields, engine_fields
from polog.field import field as FieldClass
from polog.data_structures.wrappers.fields_container.container import FieldsContainer


class FunctionLogger:
    """
    Экземпляры данного класса - декораторы, включающие автоматическое логирование для функций.
    """

    def __init__(self, settings=SettingsStore(), handlers=global_handlers, in_place_fields=in_place_fields, engine_fields=engine_fields):
        self.settings = settings
        self.engine = Engine()
        self.global_handlers = handlers
        self.in_place_fields = in_place_fields
        self.engine_fields = engine_fields

    def __call__(self, *args, message=None, level=None, errors_level=None, is_method=False, handlers=None, extra_fields=None, extra_engine_fields=None):
        """
        Фабрика декораторов логирования для функций. Можно вызывать как со скобками, так и без.
        """
        if message is not None and not isinstance(message, str):
            raise ValueError('The message of the decorator must be an instance of the str type.')
        if level is not None and not isinstance(level, int) and not isinstance(level, str):
            raise ValueError('The level of the decorator must be an instance of the str or int.')
        if errors_level is not None and not isinstance(errors_level, int) and not isinstance(errors_level, str):
            raise ValueError('The errors_level of the decorator must be an instance of the str or int.')
        if not isinstance(is_method, bool):
            raise ValueError('The flag "is_method" of the decorator must be an instance of the bool.')
        
        def error_logger(func):
            # Если функция уже ранее была задекорирована, мы декорируем ее саму, а не ее в уже задекорированном виде.
            func, before_change_func = RegisteringFunctions().get_original(func), func
            local_handlers = self.get_handlers(handlers)
            in_place_fields = self.get_extra_fields(extra_fields, self.in_place_fields)
            engine_fields = self.get_extra_fields(extra_engine_fields, self.engine_fields)
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                """
                Обертка для корутинных функций, вызов обернутой функции происходит через await.
                """
                _message._clean_context()
                args_dict = self.get_base_args_dict(func, message)
                try:
                    start = time.time()
                    args_dict['time'] = datetime.datetime.now()
                    result = await func(*args, **kwargs)
                except Exception as e:
                    finish = time.time()
                    self.log_exception_info(e, finish, start, args_dict, errors_level, level, local_handlers, in_place_fields, engine_fields, *args, **kwargs)
                    raise e
                finish = time.time()
                self.log_normal_info(result, finish, start, args_dict, level, local_handlers, in_place_fields, engine_fields, *args, **kwargs)
                return result
            @wraps(func)
            def wrapper(*args, **kwargs):
                """
                Обертка для обычных функций.
                """
                _message._clean_context()
                args_dict = self.get_base_args_dict(func, message)
                try:
                    start = time.time()
                    args_dict['time'] = datetime.datetime.now()
                    result = func(*args, **kwargs)
                except Exception as e:
                    finish = time.time()
                    self.log_exception_info(e, finish, start, args_dict, errors_level, level, local_handlers, in_place_fields, engine_fields, *args, **kwargs)
                    raise e
                finish = time.time()
                self.log_normal_info(result, finish, start, args_dict, level, local_handlers, in_place_fields, engine_fields, *args, **kwargs)
                return result
            if inspect.iscoroutinefunction(func):
                result = async_wrapper
            else:
                result = wrapper
            # Проверяем, что функцию не запрещено декорировать. Если запрещено - возвращаем оригинал, иначе - какой-то из wrapper'ов.
            result = RegisteringFunctions().get_function_or_wrapper(func, before_change_func, result, is_method)
            return result
        # Определяем, как вызван декоратор - как фабрика декораторов (т. е. без позиционных аргументов) или как непосредственный декоратор.
        if not len(args):
            return error_logger
        elif len(args) == 1 and callable(args[0]):
            return error_logger(args[0])
        raise IncorrectUseOfTheDecoratorError('You used the logging decorator incorrectly. Read the documentation.')

    def get_base_args_dict(self, function, message):
        """
        При каждом вызове функции с логирующим декоратором создается словарь с аргументами, которые будут переданы в очередь для обработчиков.
        В этой функции данный словарь инициализируется и заполняется значениями, которые уже известны еще до запуска задекорированной функции.
        """
        args_dict = {}
        args_dict['auto'] = True
        if message is not None:
            args_dict['message'] = str(message)
        self.get_arg(function, args_dict, '__module__')
        self.get_arg(function, args_dict, '__name__', key_name='function')
        not_none_to_dict(args_dict, 'class', self.get_class_name(function))
        return args_dict

    def get_class_name(self, function):
        """
        Получаем имя класса из объекта метода. Если функция не принадлежит к какому-то классу, возвращаем None.
        """
        try:
            return function.__self__.__name__
        except AttributeError:
            try:
                maybe_class_name = function.__qualname__.split('.')[-2]
                if maybe_class_name.isidentifier():
                    return maybe_class_name
            except (AttributeError, IndexError):
                pass

    @staticmethod
    def get_arg(obj, args, arg_name, key_name=None):
        """
        Извлекаем какой-то атрибут объекта по имени, после чего используем то же самое имя в качестве ключа для словарика, где в качестве значения этот объект сохраним.
        Перед использованием в качестве ключа удаляем из него дандеры.
        Если в объекте атрибут с данным именем отсутствует, в словарь ничего сохранено не будет.

        Аргументы:

        obj - исходный объект, из которого извлекаются данные.
        args - словарь, куда мы сохраняем данные.
        arg_name - строка с названием атрибута, который мы извлекаем.
        key_name (опционально) - ключ для сохранения извлеченного из obj атрибута в словаре args. Если данный параметр не задать, используется arg_name без дандеров.
        """
        if key_name is None:
            key_name = arg_name.replace('_', '')
        arg = getattr(obj, arg_name, None)
        not_none_to_dict(args, key_name, arg)

    def log_exception_info(self, exc, finish, start, args_dict, errors_level, simple_level, handlers, in_place_fields, engine_fields, *args, **kwargs):
        """
        Здесь происходит заполнение автоматически извлекаемых полей в случае исключения.
        В т. ч. извлекается вся информация об исключении - название, сообщение и т. д.
        """
        if not hasattr(exc, 'checked_by_polog') or not self.settings['deduplicate_errors']:
            exc.checked_by_polog = True
            errors_level = get_errors_level(errors_level, simple_level)
            if errors_level >= self.settings['level']:
                exception_to_dict(args_dict, exc)
                args_dict['success'] = False
                args_dict['traceback'] = get_traceback()
                args_dict['local_variables'] = get_locals_from_traceback()
                args_dict['time_of_work'] = finish - start
                args_dict['level'] = errors_level
                service_name = self.settings['service_name']
                if service_name is not None:
                    args_dict['service_name'] = service_name
                input_variables = json_vars(*args, **kwargs)
                _message._copy_context(args_dict)
                if not (input_variables is None):
                    args_dict['input_variables'] = input_variables
                log = self.create_log_item(args, kwargs, args_dict, handlers, engine_fields, in_place_fields)
                self.engine.write(log)

    def log_normal_info(self, result, finish, start, args_dict, level, handlers, in_place_fields, engine_fields, *args, **kwargs):
        """
        Заполнение автоматических полей в случае, когда исключения не было.
        """
        level = self.resolve_normal_level(level)

        if level >= self.settings['level']:
            args_dict['success'] = True
            args_dict['result'] = json_one_variable(result)
            args_dict['time_of_work'] = finish - start
            args_dict['level'] = level
            service_name = self.settings['service_name']
            if service_name is not None:
                args_dict['service_name'] = service_name
            _message._copy_context(args_dict)
            input_variables = json_vars(*args, **kwargs)
            if not (input_variables is None):
                args_dict['input_variables'] = input_variables
            log = self.create_log_item(args, kwargs, args_dict, handlers, engine_fields, in_place_fields)
            self.engine.write(log)

    def resolve_normal_level(self, level):
        """
        Определяем уровень события.
        Если клиент определил его сам - используем эту оценку. Если нет - берем дефолтное значение из настроек.
        """
        if level is not None:
            level = Levels.get(level)
        else:
            level = self.settings['default_level']
        return level

    def create_log_item(self, args, kwargs, data, handlers, engine_fields, in_place_fields):
        """
        Здесь порождается объект лога.

        К моменту вызова данного метода все данные для лога уже должны быть собраны. После конструирования объекта лога здесь, его изменение в других местах уже не предполагается.
        """
        log = LogItem()
        log.set_data(data)
        log.set_function_input_data(args, kwargs)
        log.set_handlers(handlers)
        log.set_extra_fields(engine_fields)
        log.extract_extra_fields_from(in_place_fields)
        return log

    def get_handlers(self, handlers):
        """
        Создание локального пространства имен для конкретного декоратора.

        Метод в любом случае (если в него не передали что-то невиданное) должен вернуть дерево (экземпляр NamedTree).
        Если пользователь не передал своих обработчиков вообще, импользуется глобальное дерево с обработчиками.
        Если пользователь передал коллекцию обработчиков, на базе этой коллекции конструируется новое дерево.

        В коллекции обработчиков, переданной пользователем, может быть 2 вида объектов:
        1. Сами обработчики.
        2. Пути к обработчикам в глобальном пространстве имен.

        Сначала обрабатываются пути к обработчикам. Создается новое дерево, и ноды из дерева, содержащего глобальное пространство имен обработчиков, переносятся в него по тем же путям. Таким образом обеспечивается полная преемственность соответствующих веток дерева с глобальным пространством имен - даже если там появятся новые ноды в тех же ветках, что были скопированы, они будут добавлены и в производные деревья тоже.
        Затем в новое дерево добавляются "отдельно стоящие" обработчики. Для каждого из них придумывается новое имя в локальном пространстве имен, которое ранее еще не было занято. При этом нужно учитывать, что, если уже после срабатывания кода данного метода в глобальном пространстве имен вдруг появится элемент под тем же именем, в локальное пространство он уже не попадет, т.к. был здесь "перезаписан".
        """
        if handlers is None:
            return self.global_handlers
        if not isinstance(handlers, list) and not isinstance(handlers, tuple):
            raise ValueError(f'A collection of handlers is expected. You passed "{handlers}". The collection can only be a tuple or a list.')

        is_handlers = []
        is_paths = []

        for maybe_handler in handlers:
            if isinstance(maybe_handler, str):
                is_paths.append(maybe_handler)
            elif SignatureMatcher.is_handler(maybe_handler, raise_exception=False):
                is_handlers.append(maybe_handler)
            else:
                raise HandlerNotFoundError(f'As a handler, you can pass the handler itself or its name from the global handler tree. You passed "{maybe_handler}".')

        projector = TreeProjector(self.global_handlers)

        local_scope_tree = projector.on(is_paths)

        names_generator = PonyNamesGenerator().get_next_pony()
        for handler in is_handlers:
            while True:
                new_name = next(names_generator).replace(' ', '_')
                if new_name not in local_scope_tree:
                    break
            local_scope_tree[new_name] = handler

        return local_scope_tree

    def get_extra_fields(self, maybe_fields, default_fields):
        """
        Здесь определяется набор дополнительных полей, который будет извлекаться в данном декораторе.

        maybe_fields - словарь с ключами-строками и значениями-полями (экземплярами класса field), либо список/кортеж с такими словарями и ellipsis'ами.
        default_fields - словарь с дефолтными дополнительными полями. Поля отсюда будут браться, если в списке maybe_fields лежал ellipsis.
        """
        if maybe_fields is None:
            return default_fields
        if not isinstance(maybe_fields, dict) and not isinstance(maybe_fields, list) and not isinstance(maybe_fields, tuple):
            raise ValueError(f'A dictionary containing log field extractors is expected. You can also pass a list or tuple containing such dictionaries and ellipsis. You passed "{maybe_fields}".')

        all_fields = [maybe_fields] if isinstance(maybe_fields, dict) else maybe_fields

        if Ellipsis in all_fields:
            is_ellipsis = True
            while Ellipsis in all_fields:
                try:
                    all_fields.pop(all_fields.index(Ellipsis))
                except ValueError:
                    break
        else:
            is_ellipsis = False

        pre_result = {}

        for fields in all_fields:
            for name, field in fields.items():
                if not isinstance(name, str):
                    raise ValueError(f'Strings should be used as keys in the dictionary of additional log fields. You passed: "{name}".')
                if not isinstance(field, FieldClass):
                    raise ValueError(f'An object of the field class is expected as a field object. You passed: "{field}".')
                if name in pre_result:
                    raise ValueError(f'Field name conflict. You have used the name "{name}" more than once.')

                pre_result[name] = field

        if not is_ellipsis:
            return FieldsContainer(pre_result, {})

        return FieldsContainer(pre_result, default_fields)


flog = FunctionLogger()
