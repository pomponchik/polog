import time
import asyncio
import pytest
from polog import flog, config, LoggedError, field
from polog.loggers.auto.function_logger import FunctionLogger
from polog.utils.json_vars import json_one_variable


def test_empty(handler):
    """
    Проверяем, что лог через flog записывается.
    """
    @flog(message='base text')
    def function():
        return True
    handler.clean()
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
    handler.clean()
    config.set(level=1)
    asyncio.run(function())
    time.sleep(0.001)
    log = handler.last
    assert log is not None
    assert log['module'] == function.__module__
    assert log['function'] == function.__name__

def test_message(handler):
    """
    Проверяем, что сообщение по умолчанию записывается.
    """
    @flog(message='base text')
    def function():
        return True
    handler.clean()
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
    handler.clean()
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
    handler.clean()
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
        flog.log_exception_info(e, 1.0, 0.5, data, 7)
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
    flog.log_normal_info('kek', 1.0, 0.5, data, 7)
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

def test_extract_extra_fields_base():
    """
    Проверяем, что в базовом случае дополнительные поля извлекаются.
    """
    def extractor_1(args, **kwargs):
        return 'hello'
    def extractor_2(args, **kwargs):
        return 'world'
    class FalseSettingsStore:
        extra_fields = {'hello': field(extractor_1), 'world': field(extractor_2)}
    args_dict = {}
    local_flog = FunctionLogger(settings=FalseSettingsStore())
    local_flog.extract_extra_fields(None, args_dict)
    assert args_dict == {'hello': 'hello', 'world': 'world'}

def test_extract_extra_fields_other_type_with_converter():
    """
    Проверяем, что все работает, если экстрактор поля возвращает не строковый объект, но используется конвертер.
    """
    def extractor_1(args, **kwargs):
        return 1
    def extractor_2(args, **kwargs):
        return 2
    class FalseSettingsStore:
        extra_fields = {'1': field(extractor_1, converter=lambda x: str(x) + ' converted'), '2': field(extractor_2, converter=lambda x: str(x) + ' converted')}
    args_dict = {}
    local_flog = FunctionLogger(settings=FalseSettingsStore())
    local_flog.extract_extra_fields(None, args_dict)
    assert args_dict == {'1': '1 converted', '2': '2 converted'}

def test_extract_extra_fields_other_type_without_converter():
    """
    Проверяем, что все работает, если экстрактор поля возвращает не строковый объект, и конвертер не используется.
    """
    def extractor_1(args, **kwargs):
        return 1
    def extractor_2(args, **kwargs):
        return 2
    class FalseSettingsStore:
        extra_fields = {'1': field(extractor_1), '2': field(extractor_2)}
    args_dict = {}
    local_flog = FunctionLogger(settings=FalseSettingsStore())
    local_flog.extract_extra_fields(None, args_dict)
    assert args_dict == {'1': '1', '2': '2'}
