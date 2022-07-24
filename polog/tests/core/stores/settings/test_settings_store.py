import json
from multiprocessing import Process, Queue

import pytest
import ujson

from polog import log, config
from polog.core.stores.settings.settings_store import SettingsStore


def test_set_and_get():
    """
    Проверяем, что параметры назначаются.
    """
    all_values = [
        {
            'pool_size': 7,
            'original_exceptions': False,
            'level': 5,
            'service_name': 'lol',
            'default_error_level': 7,
            'max_delay_before_exit': 5,
        },
        {
            'pool_size': 12,
            'original_exceptions': True,
            'level': 3,
            'service_name': 'kek',
            'default_error_level': 12,
            'max_delay_before_exit': 3,
        },
    ]
    store = SettingsStore()
    for values in all_values:
        for key, value in values.items():
            store[key] = value
            assert store[key] == value

def test_set_error_values():
    """
    Проверяем, что при попытке изменить значение параметра на невозможный поднимается исключение.
    """
    all_values = {
        'pool_size': [1.4, None, 'kek', -100],
        'original_exceptions': [None, 'no', 7, 1.5],
        'level': [1.2, None, -6],
        'service_name': [1.2, None],
        'default_error_level': [1.2, None, -5],
        'max_delay_before_exit': ['kek', None, -1],
        'json_module': ['kek', 1, lambda x: 'kek'],
    }
    store = SettingsStore()
    for key, local_values in all_values.items():
        for value in local_values:
            with pytest.raises(ValueError):
                store[key] = value

def test_error_keys():
    """
    Проверяем, что при использовании неправильного ключа - поднимется KeyError.
    """
    store = SettingsStore()
    with pytest.raises(KeyError):
        value = store['lol']
    with pytest.raises(KeyError):
        store['lol'] = 'kek'

def test_share_lock_specific():
    """
    Проверяем, что между полями, где локи должны быть пошарены, они пошарены.
    """
    store = SettingsStore()
    assert store.get_point('pool_size').lock is store.get_point('max_queue_size').lock
    assert store.get_point('pool_size').lock is store.get_point('started').lock

def test_conflicts_specific():
    """
    Проверяем, что нельзя выставить ненулевой размер очереди, если у пула потоков размер 0.
    А также, что нельзя выставить пулу потоков нулевой размер, если очередь ненулевая.
    """
    store = SettingsStore()
    store['max_queue_size'] = 0
    store['pool_size'] = 0

    with pytest.raises(ValueError):
        store['max_queue_size'] = 1
    store['pool_size'] = 2
    store['max_queue_size'] = 1

    with pytest.raises(ValueError):
        store['pool_size'] = 0
    store['max_queue_size'] = 0
    store['pool_size'] = 0

    store['pool_size'] = 4

def test_set_json_module():
    """
    Пробуем зарегистрировать альтернативный модуль json.
    """
    store = SettingsStore()
    assert store['json_module'] is json
    store['json_module'] = ujson
    assert store['json_module'] is ujson
    store['json_module'] = json
    assert store['json_module'] is json

@pytest.mark.parametrize("field_name", [
    'pool_size',
    'level',
    'default_level',
    'default_error_level',
    'max_queue_size',
    'started',
    'original_exceptions',
    'service_name',
    'silent_internal_exceptions',
    'max_delay_before_exit',
    'delay_on_exit_loop_iteration_in_quants',
    'time_quant',
    'engine',
    'json_module',
])
def test_operator_in(field_name):
    """
    Проверяем, что оператор in работает корректно.
    Он должен возвращать bool-значение, в зависимости от существования данного пункта настроек.
    """
    store = SettingsStore()

    assert field_name in store
    assert 'kek' not in store

def test_store_to_string():
    """
    Проверяем, что состояние настроек выводится корректно.
    """
    store = SettingsStore()
    store_string = str(store)

    assert store_string.startswith('<SettingStore object with data: ')
    assert store_string.endswith('>')

    for key in store.points:
        value = store.force_get(key)
        if isinstance(value, str):
            value = f'"{value}"'
        assert f'{key} = {value}'

def write_started_flag(queue):
    """
    Вспомогательная функция для теста test_started_flag_is_working().
    Предназначена для запуска в другом процессе с целью обнуления возможных аффектов тестов для на друга.
    """
    store = SettingsStore()

    result = [SettingsStore()['started']]

    log('kek')

    result.append(SettingsStore()['started'])

    queue.put(result)

def test_started_flag_is_working():
    """
    Проверяем, что флаг "started" действительно проставляется в значение True после записи первого лога.
    Для этого запускаем запись лога в отдельном процессе.
    """
    queue = Queue()

    process = Process(target=write_started_flag, args=(queue, ))
    process.start()
    process.join()

    assert queue.get() == [False, True]

def write_started_flag_after_reloading(queue):
    """
    Вспомогательная функция для теста test_started_flag_is_not_affected_by_engine_reloading().
    Предназначена для запуска в другом процессе с целью обнуления возможных аффектов тестов для на друга.
    """
    store = SettingsStore()

    result = [SettingsStore()['started']]

    config.set(pool_size=2)
    config.set(pool_size=3)
    config.set(pool_size=4)
    config.set(pool_size=0)

    result.append(SettingsStore()['started'])

    queue.put(result)

def test_started_flag_is_not_affected_by_engine_reloading():
    """
    Проверяем, что перезагрузка движка не аффектит флаг "started". Он может измениться только в результате записи первого лога.
    """
    queue = Queue()

    process = Process(target=write_started_flag_after_reloading, args=(queue, ))
    process.start()
    process.join()

    assert queue.get() == [False, False]
