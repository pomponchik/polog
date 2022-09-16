import time
import asyncio
from threading import get_native_id
from datetime import datetime

import pytest

from polog import flog, config, field
from polog.loggers.auto.function_logger import FunctionLogger
from polog.core.stores.settings.settings_store import SettingsStore
from polog.data_structures.trees.named_tree.tree import NamedTree
from polog.utils.json_vars import json_one_variable
from polog.core.log_item import LogItem
from polog.core.utils.exception_escaping import exception_escaping


def test_empty(handler):
    """
    Проверяем, что лог через flog записывается.
    """
    @flog(message='base text')
    def function():
        return True

    config.set(level=1)

    function()
    time.sleep(0.0001)

    assert handler.last is not None
    assert handler.last['module'] == function.__module__
    assert handler.last['function'] == function.__name__

def test_empty_async(handler):
    """
    Проверяем, что лог через flog записывается (для корутин).
    """
    @flog(message='base text')
    async def function():
        return True

    config.set(level=1)

    asyncio.run(function())
    time.sleep(0.001)

    assert handler.last is not None
    assert handler.last['module'] == function.__module__
    assert handler.last['function'] == function.__name__

def test_message(handler):
    """
    Проверяем, что сообщение по умолчанию записывается.
    """
    @flog(message='base text')
    def function():
        return True
    config.set(level=1)
    function()
    time.sleep(0.0001)
    assert handler.last['message'] == 'base text'

def test_double(handler):
    """
    Проверка, что при двойном декорировании запись генерится только одна.
    """
    @flog(message='base text 2')
    @flog(message='base text')
    def function():
        time.sleep(0.0001)
        return True

    config.set(level=1)

    function()
    time.sleep(0.0001)

    assert len(handler.all) == 1
    assert handler.last['message'] == 'base text 2'

def test_working():
    """
    Проверяем, что декоратор не ломает поведение функции.
    """
    @flog(message='base text')
    def function():
        return True
    assert function() == True

def test_working_without_brackets():
    """
    Проверяем, что декоратор можно вызывать без скобок и функция остается рабочей.
    """
    @flog
    def function():
        return True
    assert function() == True

def test_level(handler):
    """
    Проверяем, что установка уровня логирования работает.
    """
    @flog(level=7)
    def function():
        pass
    function()
    time.sleep(0.0001)
    assert handler.last['level'] == 7

def test_level_async(handler):
    """
    Проверяем, что установка уровня логирования работает.
    """
    @flog(level=7)
    async def function():
        pass

    asyncio.run(function())

    time.sleep(0.0001)
    assert handler.last['level'] == 7

def test_level_name(handler):
    """
    Проверяем, что установка уровня логирования идентификатором в виде строки работает.
    """
    config.set(level=1)
    @flog(level='lolkeklolkeklol')
    def function():
        pass

    config.levels(lolkeklolkeklol=88)
    function()
    time.sleep(0.0001)

    assert handler.last['level'] == 88

    config.levels(lolkeklolkeklol=77)
    function()
    time.sleep(0.0001)

    assert handler.last['level'] == 77

def test_get_base_args_dict():
    """
    Проверяем извлечение базовой информации из функции.
    """
    args = flog.get_base_args_dict(test_get_base_args_dict, 'kek')
    assert args['auto'] == True
    assert args['message'] == 'kek'
    assert args['function'] == test_get_base_args_dict.__name__
    assert args['module'] == test_get_base_args_dict.__module__

def test_get_arg_base_empty(empty_class):
    """
    Проверка, что, если в исходном объекте нет нужного атрибута, ничего не происходит.
    """
    data = {}
    obj = empty_class()
    flog.get_arg(obj, data, 'lol')
    assert data == {}

def test_get_arg_base_full(empty_class):
    """
    Проверка, что все извлекается.
    """
    data = {}
    obj = empty_class()
    obj.lol = 'kek'
    flog.get_arg(obj, data, 'lol')
    assert data['lol'] == 'kek'

def test_get_arg_base_full_handle_key(empty_class):
    """
    Проверка, что ключ подменяется вручную.
    """
    data = {}
    obj = empty_class()
    obj.lol = 'kek'
    flog.get_arg(obj, data, 'lol', key_name='cheburek')
    assert data['cheburek'] == 'kek'
    assert data.get('lol') is None

def test_get_arg_base_full_dander(empty_class):
    """
    Проверка, что из дандер-атрибутов все извлекается, но в словарь сохраняется без дандеров.
    """
    data = {}
    obj = empty_class()
    obj.__lol__ = 'kek'
    flog.get_arg(obj, data, '__lol__')
    assert data['lol'] == 'kek'

def test_raise_deduplicate_errors(handler):
    """
    При настройке deduplicate_errors=True сообщение записывается только при первом проходе исключения через декоратор.
    """
    config.set(deduplicate_errors=True, pool_size=0)

    @flog
    def b():
        raise ValueError
    @flog
    def a():
        return b()

    with pytest.raises(ValueError):
        a()

    assert len(handler.all) == 1

def test_raise_deduplicate_errors_async(handler):
    """
    Тест, аналогичный test_raise_deduplicate_errors, но для корутинных функций.
    """
    config.set(deduplicate_errors=True, pool_size=0)

    @flog
    async def b():
        raise ValueError
    @flog
    async def a():
        return await b()

    with pytest.raises(ValueError):
        asyncio.run(a())

    assert len(handler.all) == 1

def test_raise_not_deduplicate_errors(handler):
    """
    При настройке deduplicate_errors=False исключение, поднимающееся по стеку вызовов, записывается столько раз, сколько проходит через логирующий декоратор.
    """
    config.set(deduplicate_errors=False, pool_size=0)

    @flog
    def b():
        raise ValueError
    @flog
    def a():
        return b()

    with pytest.raises(ValueError):
        a()

    assert len(handler.all) == 2

def test_raise_not_deduplicate_errors_async(handler):
    """
    Тест, аналогичный test_raise_not_deduplicate_errors, но для корутинных функций.
    """
    config.set(deduplicate_errors=False, pool_size=0)

    @flog
    async def b():
        raise ValueError
    @flog
    async def a():
        return await b()

    with pytest.raises(ValueError):
        asyncio.run(a())

    assert len(handler.all) == 2

def test_log_exception_info():
    """
    Проверяем, что базовая информация об исключении извлекается.
    """
    data = {}
    try:
        raise ValueError('lol')
    except Exception as e:
        flog.log_exception_info(e, 1.0, 0.5, data, 7, 5,[], {}, {})
    assert data['exception_type'] == 'ValueError'
    assert data['exception_message'] == 'lol'
    assert data['time_of_work'] == 0.5
    assert data['level'] == 7
    assert data['success'] == False
    assert len(data['traceback']) > 0
    assert len(data['local_variables']) > 0
    assert data.get('message') is None
    assert data.get('input_variables') is None
    assert data.get('function') is None
    assert data.get('module') is None
    assert data.get('result') is None

def test_log_normal_info():
    """
    Проверяем, что базовая информация извлекается.
    """
    data = {}
    flog.log_normal_info('kek', 1.0, 0.5, data, 7, [], {}, {})
    assert data.get('exception_type') is None
    assert data.get('exception_message') is None
    assert data['time_of_work'] == 0.5
    assert data['level'] == 7
    assert data['success'] == True
    assert data.get('traceback') is None
    assert data.get('local_variables') is None
    assert data.get('message') is None
    assert data.get('input_variables') is None
    assert data.get('function') is None
    assert data.get('module') is None
    assert data.get('result') == json_one_variable('kek')

def test_project_tree_of_handlers_from_global_scope_of_names(handler):
    """
    Проверяем корректность отделения локального пространства имен обработчиков из глобального.
    """
    global_tree = NamedTree()
    global_tree['lol'] = handler
    global_tree['lol.kek'] = handler
    global_tree['lol.kek.cheburek'] = handler
    global_tree['perekek'] = handler

    local_tree = FunctionLogger(settings=SettingsStore(), handlers=global_tree).get_handlers([handler, 'lol'])

    assert len(local_tree) == 4
    assert 'perekek' not in local_tree
    assert 'lol' in local_tree
    assert 'lol.kek' in local_tree
    assert 'lol.kek.cheburek' in local_tree

    assert 'lol.kek.cheburek.perekekoperekek' not in local_tree
    global_tree['lol.kek.cheburek.perekekoperekek'] = handler
    assert 'lol.kek.cheburek.perekekoperekek' in local_tree

def test_project_full_tree_of_handlers_from_global_scope_of_names(handler):
    """
    Проверяем, что если список хендлеров не передан, используется глобальное пространство имен.
    """
    global_tree = NamedTree()

    local_tree = FunctionLogger(settings=SettingsStore(), handlers=global_tree).get_handlers(None)

    assert local_tree is global_tree

def test_project_tree_of_root_of_global_scope_of_names():
    """
    Пробуем забрать глобальное пространство имен целиком.
    """
    global_tree = NamedTree()

    with pytest.raises(ValueError):
        local_tree = FunctionLogger(settings=SettingsStore(), handlers=global_tree).get_handlers(['.'])

def test_local_handlers_is_working():
    """
    Проверяем, что можно указать функции локальное пространство имен и обработчики из него будут работать.
    """
    logs = []
    def local_handlers(log):
        logs.append(log)
    @flog(handlers=[local_handlers])
    def function(a, b):
        return a + b

    function(1, 2)
    time.sleep(0.00001)
    assert len(logs) == 1

def test_local_handlers_is_working_async():
    """
    Проверяем, что можно указать асинхронной функции локальное пространство имен и обработчики из него будут работать.
    """
    logs = []
    def local_handlers(log):
        logs.append(log)
    @flog(handlers=[local_handlers])
    async def function(a, b):
        return a + b

    asyncio.run(function(1, 2))
    time.sleep(0.00001)
    assert len(logs) == 1

def test_local_handlers_wrong_handlers():
    """
    Пробуем в качестве обработчика добавить неподходящий объект (не обработчик и не строку), ожидаем, что поднимется ValueError.
    """
    handlers_collection = [
        ['.'],
        [1],
        'kek',
        1,
        {},
        set(),
    ]
    for handlers in handlers_collection:
        with pytest.raises(ValueError):
            @flog(handlers=handlers)
            def function(a, b):
                return a + b

def test_create_log_item_in_flog():
    """
    Проверяем, что лог создается и наполняется переданными данными.
    """
    args = (1, 2, 3)
    kwargs = {'cheburek': 'cheburekocheburek'}
    data = {'lol': 'kek'}
    handlers = NamedTree()

    log = flog.create_log_item(args, kwargs, data, handlers, {}, {})

    assert isinstance(log, LogItem)
    assert log['lol'] == 'kek'
    assert log.get_handlers() is handlers
    assert log.function_input_data.args is args
    assert log.function_input_data.kwargs is kwargs

def test_extract_extra_fields_locally_in_the_function_decorator(handler):
    """
    Пробуем указать словарь с дополнительными полями в декораторе.
    Эти поля должны извлекаться.
    """
    def exctractor(log_item):
        return 'lol'
    @flog(extra_fields={'lolkek': field(exctractor)})
    def function():
        pass

    function()
    time.sleep(0.0001)

    assert handler.last['lolkek'] == 'lol'

def test_extract_extra_fields_locally_in_the_function_decorator_async(handler):
    """
    Пробуем указать словарь с дополнительными полями в декораторе вокруг корутинной функции.
    Эти поля должны извлекаться.
    """
    def exctractor(log_item):
        return 'lol'
    @flog(extra_fields={'lolkek': field(exctractor)})
    async def function():
        pass

    asyncio.run(function())
    time.sleep(0.0001)

    assert handler.last['lolkek'] == 'lol'

def test_extract_extra_engine_fields_in_the_function_decorator(handler):
    """
    Пробуем указать словарь с дополнительными полями в декораторе для извлечения в движке.
    Эти поля должны извлекаться.
    """
    def exctractor(log_item):
        return 'lol'

    @flog(extra_engine_fields={'lolkek': field(exctractor)})
    def function():
        pass

    function()
    time.sleep(0.0001)

    assert handler.last['lolkek'] == 'lol'

def test_compare_engine_thread_native_id_and_local(handler):
    """
    Доказываем, что поля extra_fields извлекаются в том же потоке, в котором вызывался логгер, а extra_engine_fields (при условии использования многопоточного движка) - в каком-то другом потоке.
    """
    config.set(pool_size=2, level=0)

    def exctractor(log_item):
        return get_native_id()

    @flog(extra_engine_fields={'lol': field(exctractor)}, extra_fields={'kek': field(exctractor)})
    def function():
        pass

    function()
    time.sleep(0.0001)

    assert handler.last['lol'] is not None
    assert handler.last['lol'] != handler.last['kek']
    assert handler.last['kek'] == get_native_id()

    config.set(pool_size=0)

    function()

    assert handler.last['lol'] == handler.last['kek']
    assert handler.last['lol'] == get_native_id()

def test_multiple_extra_fields_dicts(handler):
    """
    Проверяем, что при передаче списка из нескольких словарей, поля задействуются из обоих.
    Делаем две проверки: для extra_fields и для extra_engine_fields.
    """
    # На всякий случай чистим глобальные хранилища полей.
    config.delete_engine_fields(*(config.get_engine_fields().keys()))
    config.delete_fields(*(config.get_in_place_fields().keys()))

    config.set(pool_size=0)

    def exctractor_1(log_item):
        return 1
    def exctractor_2(log_item):
        return 2

    for name in ('extra_fields', 'extra_engine_fields'):
        kwargs = {
            name: [{'lol': field(exctractor_1)}, {'kek': field(exctractor_2)}],
        }

        @flog(**kwargs)
        def function():
            pass

        function()

        assert handler.last['lol'] == 1
        assert handler.last['kek'] == 2

        handler.clean()

def test_multiple_extra_fields_dicts_and_ellipsis(handler):
    """
    Проверяем, что троеточие (ellipsis) не влияет на извлечение полей из словарей.
    Пробуем разное количество троеточий в списке, ничего не должно ломаться.
    В остальном тест идентичен test_multiple_extra_fields_dicts().
    """
    # На всякий случай чистим глобальные хранилища полей.
    config.delete_engine_fields(*(config.get_engine_fields().keys()))
    config.delete_fields(*(config.get_in_place_fields().keys()))

    config.set(pool_size=0)

    def exctractor_1(log_item):
        return 1
    def exctractor_2(log_item):
        return 2

    for name in ('extra_fields', 'extra_engine_fields'):
        for number in range(5):
            dicts = [{'lol': field(exctractor_1)}, {'kek': field(exctractor_2)}, ...]

            for _ in range(number):
                dicts.append(...)

            kwargs = {
                name: dicts,
            }

            @flog(**kwargs)
            def function():
                pass

            function()

            assert handler.last['lol'] == 1
            assert handler.last['kek'] == 2

            handler.clean()

def test_affects_to_global_fields_stores(handler):
    """
    Проверяем, что установленные локально в одном декораторе поля не влияют на глобальное хранилище дополнительных полей.
    """
    # На всякий случай чистим глобальные хранилища полей.
    config.delete_engine_fields(*(config.get_engine_fields().keys()))
    config.delete_fields(*(config.get_in_place_fields().keys()))

    config.set(pool_size=0)

    def exctractor(log_item):
        return 'kek'

    for name in ('extra_fields', 'extra_engine_fields'):
        kwargs = {
            name: {'lol': field(exctractor)},
        }

        @flog(**kwargs)
        def function():
            pass

        @flog
        def function_2():
            pass

        function_2()

        assert handler.last.get('lol') is None

        handler.clean()

def test_base_behavior_with_ellipsis(handler):
    """
    Проверяем работу троеточия (ellipsis), что срабатывают и объявленные глобально поля и локальные.
    """
    config.set(pool_size=0)

    def global_exctractor(log_item):
        return 'global'

    def local_exctractor(log_item):
        return 'local'

    config.add_fields(global_item=field(global_exctractor))

    @flog(extra_fields=[{'local': field(local_exctractor)}, ...])
    def function():
        pass

    function()

    assert handler.last['local'] == 'local'
    assert handler.last['global_item'] == 'global'

    config.delete_fields('global_item')

def test_base_behavior_without_ellipsis(handler):
    """
    Проверяем, что без троеточия (ellipsis) срабатывают только локальные поля, а глобальные не используются.
    """
    config.set(pool_size=0)

    def global_exctractor(log_item):
        return 'global'

    def local_exctractor(log_item):
        return 'local'

    config.add_fields(global_item=field(global_exctractor))

    @flog(extra_fields=[{'local': field(local_exctractor)}])
    def function():
        pass

    function()

    assert handler.last['local'] == 'local'
    assert handler.last.get('global_item') is None

    config.delete_fields('global_item')

def test_auto_flag(handler):
    """
    Проверяем, что флаг "auto" для логов, записанных через декоратор, проставляется в True.
    """
    @flog
    def function():
        pass

    function()

    assert handler.last['auto'] == True

def test_auto_flag_async(handler):
    """
    Проверяем, что флаг "auto" для логов, записанных через декоратор, проставляется в True.
    """
    @flog
    async def function():
        pass

    asyncio.run(function())

    assert handler.last['auto'] == True

def test_success_flag_when_success(handler):
    """
    Флаг "success" должен проставляться в значение True, если обернутая функция отработала без исключений.
    """
    @flog
    def function():
        pass

    function()

    assert handler.last['success'] == True

def test_success_flag_when_error(handler):
    """
    Флаг "success" должен проставляться в значение False, если внутри обернутой функции поднято исключение.
    """
    @flog
    def function():
        raise ValueError

    with pytest.raises(ValueError):
        function()

    assert handler.last['success'] == False

def test_result_is_json(handler):
    """
    Проверяем, что поле "result" содержит json с результатами работы обернутой декоратором функции.
    """
    @flog
    def function():
        return 1

    function()

    assert handler.last['result'] == SettingsStore()['json_module'].dumps({'value': 1, 'type': 'int'})

def test_local_variables_is_json(handler):
    """
    Проверяем, что поле "local_variables" содержит json с локальными переменными обернутой декоратором функции, когда в той поднимается исключение.
    """
    @exception_escaping
    @flog
    def function():
        a = 'kek'
        raise ValueError('kek')

    function()

    assert handler.last['local_variables'] == SettingsStore()['json_module'].dumps({'kwargs': {'a': {'value': 'kek', 'type': 'str'}}})

def test_traceback_is_json(handler):
    """
    Проверяем, что поле "traceback" содержит json со списком строк трейсбека обернутой декоратором функции, когда в той поднимается исключение.
    """
    @exception_escaping
    @flog
    def function():
        a = 'kek'
        raise ValueError('kek')

    function()

    assert isinstance(handler.last['traceback'], str)
    assert isinstance(SettingsStore()['json_module'].loads(handler.last['traceback']), list)

def test_setting_and_not_setting_of_service_name(handler):
    """
    Наличие ключа "service_name" в логе зависит от значения соответствующей настройки. При None ключ должен отсутствовать.
    Проверяем, что это так.
    """
    config.set(pool_size=0, service_name=None)

    @flog
    def function():
        pass
    @flog
    def error_function():
        raise ValueError

    function()

    assert 'service_name' not in handler.last

    handler.clean()

    with pytest.raises(ValueError):
        error_function()

    assert 'service_name' not in handler.last

    handler.clean()
    config.set(service_name='base')

    function()

    assert handler.last['service_name'] == 'base'

    handler.clean()

    with pytest.raises(ValueError):
        error_function()

    assert handler.last['service_name'] == 'base'


def test_all_requirement_fields_are_of_expected_classes(handler):
    """
    Проверяем, что в обычном случае (когда функция, обернутая декоратором @flog, просто вызывается и успешно отрабатывает) в логе содержатся все ожидаемые поля, а все значения этих полей относятся к ожидаемым классам.
    На всякий случай прогоняем проверку много раз.
    """
    config.set(pool_size=0, service_name='base')

    number_of_tries = 10000

    @flog
    def function():
        pass

    fields = {
        'time': datetime,
        'time_of_work': float,
        'level': int,
        'auto': bool,
        'success': bool,
        'service_name': str,
        'function': str,
        'module': str,
        'result': str,
    }

    for index in range(number_of_tries):
        function()
        for field_name, expected_class in fields.items():
            assert isinstance(handler.last[field_name], expected_class)
        handler.clean()

def test_all_requirement_fields_are_of_expected_classes_when_error(handler):
    """
    Проверяем, что в обычном случае (когда функция, обернутая декоратором @flog, просто вызывается и успешно отрабатывает) в логе содержатся все ожидаемые поля, а все значения этих полей относятся к ожидаемым классам.
    На всякий случай прогоняем проверку много раз.
    """
    config.set(pool_size=0, service_name='base')

    number_of_tries = 10000

    @exception_escaping
    @flog
    def function():
        a = 'kek'
        raise ValueError('kek')

    fields = {
        'time': datetime,
        'time_of_work': float,
        'level': int,
        'auto': bool,
        'success': bool,
        'service_name': str,
        'function': str,
        'module': str,
        'exception_type': str,
        'exception_message': str,
        'traceback': str,
        'local_variables': str,
    }

    for index in range(number_of_tries):
        function()
        for field_name, expected_class in fields.items():
            assert isinstance(handler.last[field_name], expected_class)
        handler.clean()

def test_normal_log_from_decorator_does_not_contain_fields(handler):
    """
    Лог об успешной операции не должен содержать некоторые поля. Проверяем, что их действительно нет.
    """
    config.set(pool_size=0, service_name='base')

    number_of_tries = 10000

    @flog
    def function():
        pass

    fields = [
        'exception_type',
        'exception_message',
        'traceback',
        'local_variables',
    ]

    for index in range(number_of_tries):
        function()
        for field_name in fields:
            assert field_name not in handler.last
        handler.clean()

def test_level_name_converting_to_int_decorator(handler):
    """
    Проверяем, что имя уровня логирования конвертится в число.
    """
    config.levels(kek=5)

    @flog(message='kek', level='kek')
    def function():
        pass

    function()

    assert handler.last['level'] == 5

def test_level_name_converting_to_int_decorator_error(handler):
    """
    Проверяем, что имя уровня логирования конвертится в число, когда внутри обернутой функции поднимается исключение.
    """
    config.set(default_level=3, default_error_level=4)
    config.levels(kek=5)

    @exception_escaping
    @flog(message='kek', level='kek')
    def function():
        raise ValueError

    function()

    assert handler.last['level'] == 5

@flog
def simple_function():
    pass

def test_get_class_name_from_simple_function(handler):
    """
    Проверяем, что у простой функции имя класса не извлекается.
    """
    config.set(pool_size=0)

    simple_function()

    assert 'class' not in handler.last

def test_get_class_name_from_simple_local_function(handler):
    """
    Проверяем, что у функции, объявленной внутри другой функции, имя класса тоже не извлекается.
    """
    config.set(pool_size=0)

    @flog
    def function():
        pass

    function()

    assert 'class' not in handler.last

def test_get_class_name_from_method(handler):
    """
    Проверяем, что у методов имя класса извлекается.
    """
    config.set(pool_size=0)

    class KekClass:
        @flog
        def function(self):
            pass

    KekClass().function()

    assert handler.last['class'] == 'KekClass'

def test_get_class_name_from_classmethod(handler):
    """
    Проверяем, что у методов класса имя класса извлекается (при условии, что наш декоратор стоит под @classmethod).
    """
    config.set(pool_size=0)

    class KekClass:
        @classmethod
        @flog
        def function(self):
            pass

    KekClass().function()

    assert handler.last['class'] == 'KekClass'

def test_get_class_name_from_coroutine(handler):
    """
    Проверяем, что у асинхронных методов имя класса извлекается.
    """
    config.set(pool_size=0)

    class KekClass:
        @flog
        async def function(self):
            pass

    asyncio.run(KekClass().function())

    assert handler.last['class'] == 'KekClass'

def test_asyncio_result(handler):
    """
    Проверяем, что результат, возвращаемый корутиной, корректно записывается в лог.
    """
    config.set(pool_size=0)

    @flog
    async def function(a, b):
        return a + b

    result = asyncio.run(function(1, 2))

    assert result == 3
    assert handler.last['result'] == json_one_variable(3)

def test_asyncio_exception(handler):
    """
    Проверяем, что при исключении в корутинной функции информация корректно записывается в лог.
    """
    config.set(pool_size=0)

    message = 'kek message'

    @exception_escaping
    @flog
    async def function(a, b):
        raise ValueError(message)

    result = asyncio.run(function(1, 2))

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == message

def test_resolve_normal_level():
    """
    Проверяем, что определение уровня обычного события работает.
    """
    assert flog.resolve_normal_level(None) == flog.settings['default_level']
    assert flog.resolve_normal_level(5) == 5
    assert flog.resolve_normal_level(10) == 10
    assert flog.resolve_normal_level(777) == 777

    config.levels(kek=5)
    assert flog.resolve_normal_level('kek') == 5

    config.levels(kek=10)
    assert flog.resolve_normal_level('kek') == 10

def test_default_level_in_decorator(handler):
    """
    По дефолту уровень лога в декораторе должен браться из настроек, но клиент может переопределить.
    Проверяем, что это так и работает.
    """
    config.set(pool_size=0, level=0, default_level=5)

    @flog(level=10)
    def function_1():
        pass

    @flog
    def function_2():
        pass

    function_1()
    assert handler.last['level'] == 10

    function_2()
    assert handler.last['level'] == 5

    config.set(default_level=8)
    function_2()
    assert handler.last['level'] == 8

def test_set_arguments_not_allowed_types():
    """
    Проверяем, что нельзя установить:
    1. Не-строку в качестве сообщения в декораторе.
    2. Что-то кроме целых чисел и строк в качестве уровней (обычного и для ошибок).
    3. В качестве флага is_method не-булевое значение.
    """
    with pytest.raises(ValueError):
        @flog(message=10)
        def function():
            pass

    with pytest.raises(ValueError):
        @flog(level=1.5)
        def function():
            pass

    with pytest.raises(ValueError):
        @flog(errors_level=1.5)
        def function():
            pass

    with pytest.raises(ValueError):
        @flog(is_method=12)
        def function():
            pass

    with pytest.raises(ValueError):
        @flog(is_method='True')
        def function():
            pass
