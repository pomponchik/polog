import time
import pytest
from polog import config, handle_log as log, field, flog
from polog.core.settings_store import SettingsStore
from polog.core.levels import Levels


def test_set_valid_key_delay_before_exit():
    """
    Проверяем, что настройка с корректным ключом принимается и сохраняется в SettingsStore.
    """
    # delay_before_exit
    config.set(delay_before_exit=1)
    assert SettingsStore().delay_before_exit == 1
    config.set(delay_before_exit=2)
    assert SettingsStore().delay_before_exit == 2
    # service_name
    config.set(service_name='lol')
    assert SettingsStore().service_name == 'lol'
    config.set(service_name='kek')
    assert SettingsStore().service_name == 'kek'
    # level
    config.set(level=1)
    assert SettingsStore().level == 1
    config.set(level=2)
    assert SettingsStore().level == 2
    config.set(level=1)
    # errors_level
    config.set(errors_level=1)
    assert SettingsStore().errors_level == 1
    config.set(errors_level=2)
    assert SettingsStore().errors_level == 2
    # original_exceptions
    config.set(original_exceptions=True)
    assert SettingsStore().original_exceptions == True
    config.set(original_exceptions=False)
    assert SettingsStore().original_exceptions == False
    config.set(original_exceptions=True)
    # pool_size
    config.set(pool_size=1)
    assert SettingsStore().pool_size == 1
    config.set(pool_size=2)
    assert SettingsStore().pool_size == 2
    # silent_internal_exceptions
    config.set(silent_internal_exceptions=True)
    assert SettingsStore().silent_internal_exceptions == True
    config.set(silent_internal_exceptions=False)
    assert SettingsStore().silent_internal_exceptions == False

def test_set_invalid_key():
    """
    Проверяем, что неправильный ключ настройки использовать не получется и поднимется исключение.
    """
    with pytest.raises(KeyError):
        config.set(invalid_key='lol')

def test_set_invalid_value():
    """
    Проверяем, что значение настройки с неправильным типом данных использовать не получется и поднимется исключение.
    """
    with pytest.raises(ValueError):
        config.set(delay_before_exit='lol')

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
    with pytest.raises(ValueError):
        config.levels(lol=-100)
    with pytest.raises(TypeError):
        config.levels(lol=1.5)

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
    with pytest.raises(ValueError):
        config.add_handlers('lol')

def test_add_handlers_wrong_function():
    """
    Проверяем, функцию с некорректной сигнатурой невозможно добавить в качестве обработчика.
    """
    def new_handler(lol, kek):
        pass
    with pytest.raises(ValueError):
        config.add_handlers(new_handler)

def test_add_similar_handlers():
    """
    Проверяем, что один и тот же обработчик нельзя зарегистрировать дважды.
    В норме при такой попытке должно подниматься исключение.
    """
    with pytest.raises(ValueError):
        def new_handler(args, **fields):
            pass
        config.add_handlers(new_handler)
        config.add_handlers(new_handler)
    with pytest.raises(ValueError):
        def new_handler2(args, **fields):
            pass
        config.add_handlers(new_handler2, new_handler2)
    with pytest.raises(ValueError):
        def new_handler3(args, **fields):
            pass
        config.add_handlers(abc=new_handler3)
        config.add_handlers(abcd=new_handler3)


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
    assert config.get_handlers('lolkekcheburek')['lolkekcheburek'] is new_handler
    assert len(config.get_handlers('lolkekcheburek')) == 1
    assert len(config.get_handlers()) > 1

def test_delete_handlers():
    """
    Проверка удаления обработчиков.
    Должна работать как по имени, так и прямой передачей объекта.
    """
    def new_handler(args, **fields):
        pass
    def new_handler2(args, **fields):
        pass
    config.add_handlers(lolkek123=new_handler)
    config.delete_handlers('lolkek123')
    assert config.get_handlers().get('lolkek123') is None
    config.add_handlers(lolkek123=new_handler)
    config.delete_handlers(new_handler)
    assert config.get_handlers().get('lolkek123') is None
    config.add_handlers(lolkek123=new_handler, lolkek345=new_handler2)
    config.delete_handlers('lolkek123', new_handler2)
    assert config.get_handlers().get('lolkek123') is None
    assert config.get_handlers().get('lolkek345') is None

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

def test_double_name_set_handler():
    """
    Запрещено дважды пытаться присвоить одно и то же имя одному или нескольким обработчикам.
    Проверяем, что в этом случае поднимается исключение.
    """
    def local_handler(a, **b):
        pass
    with pytest.raises(KeyError):
        config.add_handlers(ggg=local_handler)
        config.add_handlers(ggg=local_handler)

def test_get_handlers_not_str():
    """
    Проверяем, что поднимается исключение, когда мы вместо имени обработчика (то есть строки) используем любой другой объект.
    """
    with pytest.raises(KeyError):
        handlers = config.get_handlers(1)

def test_delete_fields_not_str():
    """
    Проверяем, что поднимается исключение, когда мы вместо имени поля (то есть строки) используем любой другой объект.
    """
    with pytest.raises(KeyError):
        handlers = config.delete_fields(1)

def test_delete_not_existed_handler():
    """
    При попытке удалить обработчик с несуществующим именем должно подняться исключение.
    """
    with pytest.raises(KeyError):
        config.delete_handlers('lolkek123')

def test_add_wrong_field():
    """
    Проверяем, что поднимается исключение, если вместо поля скормить объект с неподходящей сигнатурой.
    """
    with pytest.raises(ValueError):
        config.add_fields(press_f='kek')

def test_delete_wrong_type_handler():
    """
    Пробуем удалить из списка обработчиков объект, который ранее не был зарегистрирован в качестве обработчика.
    """
    with pytest.raises(ValueError):
        config.delete_handlers(1)
