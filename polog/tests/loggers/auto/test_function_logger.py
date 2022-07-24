import time
import asyncio
from threading import get_native_id
from datetime import datetime

import pytest

from polog import flog, config, LoggedError, field
from polog.loggers.auto.function_logger import FunctionLogger
from polog.core.stores.settings.settings_store import SettingsStore
from polog.data_structures.trees.named_tree.tree import NamedTree
from polog.utils.json_vars import json_one_variable
from polog.core.log_item import LogItem


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
    Проверяем, декоратор можно вызывать без скобок и функция остается рабочей.
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

def test_level(handler):
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

def test_raise_original():
    """
    При настройке original_exceptions=True переподниматься должно оригинальное исключение.
    """
    config.set(original_exceptions=True)
    try:
        raise ValueError
    except Exception as e:
        try:
            flog.reraise_exception(e)
            assert False # Проверка, что исключение в принципе переподнимается.
        except Exception as e2:
            assert e is e2

def test_raise_not_original():
    """
    При настройке original_exceptions=False переподниматься должно исключение LoggedError.
    """
    config.set(original_exceptions=False)
    try:
        raise ValueError
    except Exception as e:
        with pytest.raises(LoggedError):
            flog.reraise_exception(e)

def test_log_exception_info():
    """
    Проверяем, что базовая информация об исключении извлекается.
    """
    data = {}
    try:
        raise ValueError('lol')
    except Exception as e:
        flog.log_exception_info(e, 1.0, 0.5, data, 7, [], {}, {})
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

@pytest.mark.parametrize("handlers", [
    ['.'],
    [1],
    'kek',
    1,
    {},
    set(),
])
def test_local_handlers_wrong_handlers(handlers):
    """
    Пробуем в качестве обработчика добавить неподходящий объект (не обработчик и не строку), ожидаем, что поднимется ValueError.
    """
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
    assert handler.last['kek'] == str(get_native_id())

    config.set(pool_size=0)

    function()

    assert handler.last['lol'] == handler.last['kek']
    assert handler.last['lol'] == str(get_native_id())

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

        assert handler.last['lol'] == '1'
        assert handler.last['kek'] == '2'

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

            assert handler.last['lol'] == '1'
            assert handler.last['kek'] == '2'

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
    Флаг "success" должен проставляться в значение True, если внутри обернутой функции поднято исключение.
    """
    @flog
    def function():
        raise ValueError

    with pytest.raises(ValueError):
        function()

    assert handler.last['success'] == False

def test_all_requirement_fields_are_of_expected_classes(handler):
    """
    Проверяем, что в обычном случае (когда функция, обернутая декоратором @flog, просто вызывается и успешно отрабатывает) в логе содержатся все ожидаемые поля, а все значения этих полей относятся к ожидаемым классам.
    На всякий случай прогоняем проверку много раз.
    """
    config.set(pool_size=0)

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
        'service': str,
        'function': str,
    }

    for index in range(number_of_tries):
        function()
        for field_name, expected_class in fields.items():
            assert isinstance(handler.last[field_name], expected_class)
        handler.clean()
