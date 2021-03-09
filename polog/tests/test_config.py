import time
import pytest
from polog import config, log, field, flog
from polog.core.base_settings import BaseSettings
from polog.core.levels import Levels


def test_set_valid_key_delay_before_exit():
    """
    Проверяем, что настройка с корректным ключом принимается и сохраняется в BaseSettings.
    """
    # delay_before_exit
    config.set(delay_before_exit=1)
    assert BaseSettings().delay_before_exit == 1
    config.set(delay_before_exit=2)
    assert BaseSettings().delay_before_exit == 2
    # service_name
    config.set(service_name='lol')
    assert BaseSettings().service_name == 'lol'
    config.set(service_name='kek')
    assert BaseSettings().service_name == 'kek'
    # level
    config.set(level=1)
    assert BaseSettings().level == 1
    config.set(level=2)
    assert BaseSettings().level == 2
    config.set(level=1)
    # errors_level
    config.set(errors_level=1)
    assert BaseSettings().errors_level == 1
    config.set(errors_level=2)
    assert BaseSettings().errors_level == 2
    # original_exceptions
    config.set(original_exceptions=True)
    assert BaseSettings().original_exceptions == True
    config.set(original_exceptions=False)
    assert BaseSettings().original_exceptions == False
    config.set(original_exceptions=True)
    # pool_size
    config.set(pool_size=1)
    assert BaseSettings().pool_size == 1
    config.set(pool_size=2)
    assert BaseSettings().pool_size == 2

def test_set_invalid_key():
    """
    Проверяем, что неправильный ключ настройки использовать не получется и поднимется исключение.
    """
    try:
        config.set(invalid_key='lol')
        assert False
    except KeyError:
        assert True
    except:
        assert False

def test_set_invalid_value():
    """
    Проверяем, что значение настройки с неправильным типом данных использовать не получется и поднимется исключение.
    """
    try:
        config.set(delay_before_exit='lol')
        assert False
    except TypeError:
        assert True
    except:
        assert False

def test_levels_set_good_value():
    """
    Проверяем, что уровень меняется.
    """
    config.levels(lol=100)
    assert Levels.get('lol') == 100
    config.levels(lol=200)
    assert Levels.get('lol') == 200

def test_levels_set_wrong_value():
    """
    Проверяем, что невозможно установить уровень, не являющийся целым неотрицательным числом.
    """
    try:
        config.levels(lol=-100)
        assert False
    except:
        assert True
    try:
        config.levels(lol=1.5)
        assert False
    except:
        assert True

def test_standart_levels():
    """
    Проверяем, что уровни логирования из стандартной схемы устанавливаются.
    """
    config.standart_levels()
    assert Levels.get('DEBUG') == 10
    assert Levels.get('INFO') == 20
    assert Levels.get('WARNING') == 30
    assert Levels.get('ERROR') == 40
    assert Levels.get('CRITICAL') == 50

def test_add_handlers():
    """
    Проверяем, что новый обработчик добавляется и работает.
    """
    lst = []
    def new_handler(args, **fields):
        lst.append(fields['level'])
    config.add_handlers(new_handler)
    log('lol')
    time.sleep(0.0001)
    assert len(lst) > 0

def test_add_handlers_wrong():
    """
    Проверяем, что, если попытаться скормить под видом обработчика не обработчик - поднимется исключение.
    """
    try:
        config.add_handlers('lol')
        assert False
    except:
        assert True

def test_add_handlers_wrong_function():
    """
    Проверяем, функцию с некорректной сигнатурой невозможно добавить в качестве обработчика.
    """
    def new_handler(lol, kek):
        pass
    try:
        config.add_handlers(new_handler)
        assert False
    except ValueError:
        assert True

def test_add_similar_handlers():
    """
    Проверяем, что один и тот же обработчик нельзя зарегистрировать дважды.
    """
    def new_handler(args, **fields):
        pass
    config.add_handlers(new_handler)
    handlers_number = len(config.get_handlers())
    config.add_handlers(new_handler)
    assert len(config.get_handlers()) == handlers_number
    def new_handler2(args, **fields):
        pass
    handlers_number = len(config.get_handlers())
    config.add_handlers(new_handler2, new_handler2)
    assert len(config.get_handlers()) == handlers_number + 1
    def new_handler3(args, **fields):
        pass
    config.add_handlers(abc=new_handler3)
    handlers_number = len(config.get_handlers())
    config.add_handlers(abcd=new_handler3)
    assert len(config.get_handlers()) == handlers_number

def test_get_handlers():
    """
    Проверяем, что config.get_handlers() работает с аргументами и без.
    """
    def new_handler(args, **fields):
        pass
    def new_handler2(args, **fields):
        pass
    config.add_handlers(lolkekcheburek=new_handler)
    config.add_handlers(new_handler2)
    assert 'lolkekcheburek' in config.get_handlers()
    assert config.get_handlers()['lolkekcheburek'] is new_handler
    assert len(config.get_handlers('lolkekcheburek')) == 1
    assert len(config.get_handlers()) > 1

def test_add_field(handler):
    """
    Проверяем, что кастомные поля добавляются и работают.
    """
    handler.clean()
    def extractor(args, **kwargs):
        return 'lol'
    @flog
    def function():
        pass
    config.add_fields(new_field=field(extractor))
    function()
    time.sleep(0.0001)
    assert handler.last['new_field'] == 'lol'
    config.delete_fields('new_field')

def test_delete_field(handler):
    """
    Проверяем, что кастомные поля удаляются.
    """
    handler.clean()
    def extractor(args, **kwargs):
        return 'lol'
    @flog
    def function():
        pass
    config.add_fields(new_field=field(extractor))
    config.delete_fields('new_field')
    function()
    time.sleep(0.0001)
    assert handler.last.fields.get('new_field') is None
