import time
import json
from multiprocessing import Process

import pytest
import ujson

from polog import config, handle_log, field, flog, log
from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.stores.levels import Levels
from polog.data_structures.trees.named_tree.tree import NamedTree
from polog.tests.test_config_without_log import do_log


def test_set_valid_key_delay_before_exit():
    """
    Проверяем, что настройка с корректным ключом принимается и сохраняется в SettingsStore.
    """
    # delay_before_exit
    config.set(max_delay_before_exit=1)
    assert SettingsStore()['max_delay_before_exit'] == 1
    config.set(max_delay_before_exit=2)
    assert SettingsStore()['max_delay_before_exit'] == 2
    # service_name
    config.set(service_name='lol')
    assert SettingsStore()['service_name'] == 'lol'
    config.set(service_name='kek')
    assert SettingsStore()['service_name'] == 'kek'
    # level
    config.set(level=1)
    assert SettingsStore()['level'] == 1
    config.set(level=2)
    assert SettingsStore()['level'] == 2
    config.set(level=1)
    # default_level
    config.set(default_level=1)
    assert SettingsStore()['default_level'] == 1
    config.set(default_level=2)
    assert SettingsStore()['default_level'] == 2
    # default_error_level
    config.set(default_error_level=1)
    assert SettingsStore()['default_error_level'] == 1
    config.set(default_error_level=2)
    assert SettingsStore()['default_error_level'] == 2
    # pool_size
    config.set(pool_size=1)
    assert SettingsStore()['pool_size'] == 1
    config.set(pool_size=2)
    assert SettingsStore()['pool_size'] == 2
    # silent_internal_exceptions
    config.set(silent_internal_exceptions=True)
    assert SettingsStore()['silent_internal_exceptions'] == True
    config.set(silent_internal_exceptions=False)
    assert SettingsStore()['silent_internal_exceptions'] == False
    # debug_mode
    config.set(debug_mode=True)
    assert SettingsStore()['debug_mode'] == True
    config.set(debug_mode=False)
    assert SettingsStore()['debug_mode'] == False
    # smart_assert_politic
    config.set(smart_assert_politic='all')
    assert callable(SettingsStore()['smart_assert_politic'])
    smart_assert_one = SettingsStore()['smart_assert_politic']
    config.set(smart_assert_politic='if_debug')
    assert callable(SettingsStore()['smart_assert_politic'])
    assert smart_assert_one is not SettingsStore()['smart_assert_politic']
    config.set(smart_assert_politic='all')
    assert smart_assert_one is SettingsStore()['smart_assert_politic']
    # fields_intersection
    config.set(fields_intersection=True)
    assert SettingsStore()['fields_intersection'] == True
    config.set(fields_intersection=False)
    assert SettingsStore()['fields_intersection'] == False
    # unknown_fields_in_handle_logs
    config.set(unknown_fields_in_handle_logs=True)
    assert SettingsStore()['unknown_fields_in_handle_logs'] == True
    config.set(unknown_fields_in_handle_logs=False)
    assert SettingsStore()['unknown_fields_in_handle_logs'] == False
    # deduplicate_errors
    config.set(deduplicate_errors=True)
    assert SettingsStore()['deduplicate_errors'] == True
    config.set(deduplicate_errors=False)
    assert SettingsStore()['deduplicate_errors'] == False
    config.set(deduplicate_errors=True)
    # suppress_by_default
    config.set(suppress_by_default=True)
    assert SettingsStore()['suppress_by_default'] == True
    config.set(suppress_by_default=False)
    assert SettingsStore()['suppress_by_default'] == False

def test_set_invalid_key():
    """
    Проверяем, что неправильный ключ настройки использовать не получится и поднимется исключение.
    """
    with pytest.raises(KeyError):
        config.set(invalid_key='lol')

def test_set_invalid_value():
    """
    Проверяем, что значение настройки с неправильным типом данных использовать не получится и поднимется исключение.
    """
    with pytest.raises(ValueError):
        config.set(max_delay_before_exit='lol')

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
    with pytest.raises(TypeError):
        config.levels(lol='1.5')

def test_standard_levels():
    """
    Проверяем, что уровни логирования из стандартной схемы устанавливаются.
    """
    config.standard_levels()

    assert Levels.get('NOTSET') == 0
    assert Levels.get('DEBUG') == 10
    assert Levels.get('INFO') == 20
    assert Levels.get('WARNING') == 30
    assert Levels.get('ERROR') == 40
    assert Levels.get('CRITICAL') == 50
    assert Levels.get('debug') == 10
    assert Levels.get('info') == 20
    assert Levels.get('warning') == 30
    assert Levels.get('error') == 40
    assert Levels.get('critical') == 50

def test_add_handlers():
    """
    Проверяем, что новый обработчик добавляется и работает.
    """
    config.set(pool_size=0)

    lst = []
    def new_handler(log):
        lst.append(log['level'])

    config.add_handlers(new_handler)

    log('lol')

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

def test_config_add_handlers_dict_log_and_get():
    """
    Пробуем добавить обработчик через словарь.
    Должен добавиться и начать работать при регистрации логов.
    """
    config.set(pool_size=0)

    lst = []
    def new_handler(log):
        lst.append(log['level'])

    config.add_handlers({'new_handler': new_handler})

    log('lol')

    assert len(lst) > 0
    assert config.get_handlers()['new_handler'] is new_handler

def test_config_add_handlers_dict_wrong():
    """
    Пробуем передать словарь с неправильным содержимым.
    """
    with pytest.raises(ValueError):
        config.add_handlers({'kekoperekek': 'kekoperekek'})
    with pytest.raises(KeyError):
        config.add_handlers({'1': 'new_handler'})
    with pytest.raises(KeyError):
        config.add_handlers({1: 'new_handler'})
    with pytest.raises(KeyError):
        def kek(log_item):
            pass
        config.add_handlers({1: kek})
    with pytest.raises(ValueError):
        def kek_2(a, b):
            pass
        config.add_handlers({'kek': kek_2})

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
    def new_handler(log):
        pass
    def new_handler2(log):
        pass
    config.add_handlers(lolkekcheburek=new_handler)
    config.add_handlers(new_handler2)

    assert 'lolkekcheburek' in config.get_handlers()
    assert config.get_handlers()['lolkekcheburek'] is new_handler
    assert config.get_handlers('lolkekcheburek')['lolkekcheburek'] is new_handler
    assert len(config.get_handlers('lolkekcheburek')) == 1
    assert len(config.get_handlers()) > 1

    assert isinstance(config.get_handlers(), NamedTree)
    assert isinstance(config.get_handlers('lolkekcheburek'), NamedTree)

    with pytest.raises(KeyError):
        config.get_handlers(1)

def test_delete_handlers():
    """
    Проверка удаления обработчиков.
    Должна работать как по имени, так и прямой передачей объекта.
    """
    def new_handler(log):
        pass
    def new_handler2(log):
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
    def extractor(log):
        return 'lol'
    @flog
    def function():
        pass
    config.add_fields(new_field=field(extractor))
    function()
    time.sleep(0.0001)
    assert handler.last['new_field'] == 'lol'
    config.delete_fields('new_field')

def test_add_engine_field(handler):
    """
    Проверяем, что кастомные поля добавляются и работают.
    """
    def extractor(log):
        return 'lol'
    @log
    def function():
        pass
    config.add_engine_fields(new_field=field(extractor))
    function()
    time.sleep(0.0001)
    assert handler.last['new_field'] == 'lol'
    config.delete_engine_fields('new_field')

def test_delete_field(handler):
    """
    Проверяем, что кастомные поля удаляются.
    """
    def extractor(log):
        return 'lol'
    @log
    def function():
        pass
    config.add_fields(new_field=field(extractor))
    config.delete_fields('new_field')
    function()
    time.sleep(0.0001)
    assert handler.last.fields.get('new_field') is None

def test_delete_engine_field(handler):
    """
    Проверяем, что кастомные поля удаляются.
    """
    def extractor(log):
        return 'lol'
    @log
    def function():
        pass
    config.add_engine_fields(new_field=field(extractor))
    config.delete_engine_fields('new_field')
    function()
    time.sleep(0.0001)
    assert handler.last.fields.get('new_field') is None

def test_double_name_set_handler():
    """
    Запрещено дважды пытаться присвоить одно и то же имя одному или нескольким обработчикам.
    Проверяем, что в этом случае поднимается исключение.
    """
    def local_handler(a):
        pass
    with pytest.raises(NameError):
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

def test_delete_engine_fields_not_str():
    """
    Проверяем, что поднимается исключение, когда мы вместо имени поля (то есть строки) используем любой другой объект.
    """
    with pytest.raises(KeyError):
        handlers = config.delete_engine_fields(1)

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

def test_add_wrong_engine_field():
    """
    Проверяем, что поднимается исключение, если вместо поля для извлечения внутри движка скормить объект с неподходящей сигнатурой.
    """
    with pytest.raises(ValueError):
        config.add_engine_fields(press_f='kek')

def test_delete_wrong_type_handler():
    """
    Пробуем удалить из списка обработчиков объект, который ранее не был зарегистрирован в качестве обработчика.
    """
    with pytest.raises(ValueError):
        config.delete_handlers(1)

def test_forbidden_name_for_level():
    """
    Часть возможных имен уровней логирования зарезервированы для внутреннего использования в Polog (для имен методов) и не могут быть использованы.
    Проверяем, что при попытке определить уровень логирования с таким именем поднимется исключение.
    """
    with pytest.raises(NameError):
        config.levels(message=5)
    with pytest.raises(NameError):
        config.levels(_maybe_raise=5)
    with pytest.raises(NameError):
        config.levels(_specific_processing=5)

def test_set_log_as_built_in(filename_for_test, number_of_strings_in_the_files):
    """
    Проверяем, что использование функции log() без импорта работает.
    """
    process = Process(target=do_log, args=(filename_for_test, ))
    process.start()
    process.join()

    assert number_of_strings_in_the_files(filename_for_test) == 1

def test_set_in_place_fields_and_get_it_all():
    """
    Пробуем передать поля для извлечения "на месте" в конфиг и потом проверяем, что они же и возвращаются.
    """
    lol_field = field(lambda x: 'lol')
    kek_field = field(lambda x: 'kek')

    config.add_fields(lol=lol_field)
    config.add_fields(kek=kek_field)

    all_in_place_fields = config.get_in_place_fields()

    assert len(all_in_place_fields) >= 2
    assert all_in_place_fields['lol'] is lol_field
    assert all_in_place_fields['kek'] is kek_field

def test_set_engine_fields_and_get_it_all():
    """
    Пробуем передать поля для извлечения внутри движка в конфиг и потом проверяем, что они же и возвращаются.
    """
    lol_field = field(lambda x: 'lol')
    kek_field = field(lambda x: 'kek')

    config.add_engine_fields(lol=lol_field)
    config.add_engine_fields(kek=kek_field)

    engine_fields = config.get_engine_fields()

    assert len(engine_fields) >= 2
    assert engine_fields['lol'] is lol_field
    assert engine_fields['kek'] is kek_field

def test_set_in_place_field_and_get_it():
    """
    Пробуем передать поля для извлечения "на месте" в конфиг, после чего извлекаем по имени только одно из них.
    Проверяем, что возвращается оно и только оно.
    """
    lol_field = field(lambda x: 'lol')
    kek_field = field(lambda x: 'kek')

    config.add_fields(lol=lol_field)
    config.add_fields(kek=kek_field)

    all_in_place_fields = config.get_in_place_fields('lol')

    assert len(all_in_place_fields) == 1
    assert all_in_place_fields['lol'] is lol_field

def test_set_engine_field_and_get_it():
    """
    Пробуем передать поля для извлечения внутри движка в конфиг, после чего извлекаем по имени только одно из них.
    Проверяем, что возвращается оно и только оно.
    """
    lol_field = field(lambda x: 'lol')
    kek_field = field(lambda x: 'kek')

    config.add_engine_fields(lol=lol_field)
    config.add_engine_fields(kek=kek_field)

    engine_fields = config.get_engine_fields('lol')

    assert len(engine_fields) == 1
    assert engine_fields['lol'] is lol_field

def test_set_and_get_engine_and_in_place_fields_without_intersection():
    """
    Проверяем, что поля для извлечения сразу и внутри движка - не пересекаются.
    """
    lol_engine_field = field(lambda x: 'lol')
    kek_engine_field = field(lambda x: 'kek')
    kekburek_engine_field = field(lambda x: 'kekburek')
    assert not config.get_engine_fields('kekburek')

    lol_in_place_field = field(lambda x: 'lol')
    kek_in_place_field = field(lambda x: 'kek')
    berekuk_in_place_field = field(lambda x: 'berekuk')
    assert not config.get_in_place_fields('berekuk')

    config.add_engine_fields(lol=lol_engine_field)
    config.add_engine_fields(kek=kek_engine_field)
    config.add_engine_fields(kekburek=kekburek_engine_field)

    config.add_fields(lol=lol_in_place_field)
    config.add_fields(kek=kek_in_place_field)
    config.add_fields(berekuk=berekuk_in_place_field)

    in_place_fields = config.get_in_place_fields()
    engine_fields = config.get_engine_fields()

    assert in_place_fields['lol'] is not engine_fields['lol']
    assert in_place_fields['kek'] is not engine_fields['kek']

    assert engine_fields['lol'] is not engine_fields['kek']
    assert in_place_fields['lol'] is not in_place_fields['kek']

    assert 'kekburek' in engine_fields
    assert 'kekburek' not in in_place_fields

    assert 'berekuk' in in_place_fields
    assert 'berekuk' not in engine_fields

def test_get_all_fields_without_intersection():
    """
    Пробуем получить все дополнительные поля (то есть предназначенные как для извлечения "на месте", так и внутри движка).
    Но без пересечения имен, то есть мы не проверяем приоритет. Мы проверяем только что возвращаются все поля, которые мы передали.
    Предварительно чистим все старые поля, которые могли создаваться в рамках других тестов.
    """
    config.delete_engine_fields(*(config.get_engine_fields().keys()))
    config.delete_fields(*(config.get_in_place_fields().keys()))

    lol_engine_field = field(lambda x: 'lol')
    kek_in_place_field = field(lambda x: 'kek')

    config.add_engine_fields(lol=lol_engine_field)
    config.add_fields(kek=kek_in_place_field)

    all_fields = config.get_all_fields()

    assert len(all_fields) == 2
    assert all_fields['lol'] is lol_engine_field
    assert all_fields['kek'] is kek_in_place_field

def test_get_all_fields_without_intersection_by_names():
    """
    Проверяем то же самое, что и в test_get_all_fields_without_intersection(), но здесь нас интересует фильтрация результата.
    """
    config.delete_engine_fields(*(config.get_engine_fields().keys()))
    config.delete_fields(*(config.get_in_place_fields().keys()))

    lol_engine_field = field(lambda x: 'lol')
    kek_in_place_field = field(lambda x: 'kek')

    config.add_engine_fields(lol=lol_engine_field)
    config.add_fields(kek=kek_in_place_field)

    all_fields = config.get_all_fields('lol')

    assert len(all_fields) == 1
    assert all_fields['lol'] is lol_engine_field

    all_fields = config.get_all_fields('kek')

    assert len(all_fields) == 1
    assert all_fields['kek'] is kek_in_place_field

    all_fields = config.get_all_fields('lol', 'kek')

    assert len(all_fields) == 2
    assert all_fields['lol'] is lol_engine_field
    assert all_fields['kek'] is kek_in_place_field

def test_get_all_fields_with_intersection(handler):
    """
    Здесь проверются две вещи:
    1. При пересечении имен полей для извлечения "на месте" и внутри движка, по итогу возвращается то, что для движка.
    2. Этот порядок совпадает с реальным порядком извлечения полей внутри Polog (то есть, поскольку движковые поля извлекаются позднее, они перекрывают поля для извлечения "на месте").
    """
    config.set(pool_size=0)

    config.delete_engine_fields(*(config.get_engine_fields().keys()))
    config.delete_fields(*(config.get_in_place_fields().keys()))

    lol_engine_field = field(lambda x: 'lol_engine')
    lol_in_place_field = field(lambda x: 'lol_in_place')

    config.add_engine_fields(lol=lol_engine_field)
    config.add_fields(lol=lol_in_place_field)

    all_fields = config.get_all_fields('lol')

    assert len(all_fields) == 1
    assert all_fields['lol'] is lol_engine_field

    all_fields = config.get_all_fields()

    assert len(all_fields) == 1
    assert all_fields['lol'] is lol_engine_field

    @log
    def kek():
        pass

    config.set(fields_intersection=True)
    kek()
    assert handler.last['lol'] == 'lol_engine'

    config.set(fields_intersection=False)
    kek()
    assert handler.last['lol'] == 'lol_in_place'

def test_set_zero_level(handler):
    """
    Пробуем установить нулевой уровень в качестве базового. Должно работать.
    """
    config.set(level=0, pool_size=0)

    log('kek', level=1)

    assert handler.last is not None

def test_set_name_to_zero_level(handler):
    """
    Устанавливаем имя для нулевого уровня. Должно работать.
    """
    config.set(level=0, pool_size=0)
    config.levels(lol=0)

    log('kek', level='lol')

    assert handler.last is not None

def test_set_base_field_name():
    """
    При попытке заменить встроенные поля внешними извлекаемыми должно подниматься исключение.
    """
    with pytest.raises(NameError):
        config.add_fields(level=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(auto=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(time=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(service_name=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(success=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(function=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(module=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(message=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(exception_type=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(exception_message=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(traceback=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(input_variables=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(local_variables=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(result=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_fields(time_of_work=field(lambda x: 'kek'))

def test_set_base_engine_field_name():
    """
    При попытке заменить встроенные поля внешними извлекаемыми должно подниматься исключение.
    """
    with pytest.raises(NameError):
        config.add_engine_fields(level=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(auto=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(time=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(service_name=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(success=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(function=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(module=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(message=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(exception_type=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(exception_message=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(traceback=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(input_variables=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(local_variables=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(result=field(lambda x: 'kek'))
    with pytest.raises(NameError):
        config.add_engine_fields(time_of_work=field(lambda x: 'kek'))
