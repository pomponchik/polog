import time
from threading import active_count, Thread
from multiprocessing import Process

import pytest

from polog.core.engine.engine import Engine
from polog.core.stores.settings.settings_store import SettingsStore
from polog import config, file_writer, log
from polog.core.log_item import LogItem


def test_singleton():
    """
    Проверяем, что Writer - это синглтон.
    """
    assert Engine() is Engine()

def test_reload_threads_counting():
    """
    Проверяем, что количество потоков увеличивается в соответствии с ожидаемым увеличением пула потоков при перезагрузке движка.
    """
    engine = Engine()
    store = SettingsStore()
    engine.write({'lol': 'kek'})

    before = active_count()
    store['pool_size'] = store['pool_size'] + 2
    engine.reload()
    after = active_count()

    assert after == before + 2

def test_reload_massive_attack(handler):
    """
    Пробуем перезагрузить движок в тот момент, пока другой поток пишет логи.
    За счет блокировок ни одно событие не должно потеряться.
    """
    log = LogItem()
    log.set_handlers([handler])
    log.set_data({'lol': 'kek'})

    engine = Engine()
    store = SettingsStore()
    engine.write(log)
    time.sleep(0.0001)
    handler.clean()

    number_of_items = 3000

    def go_attack():
        for x in range(number_of_items):
            engine.write(log)
    thread = Thread(target=go_attack)
    thread.start()

    engine.reload()
    time.sleep(0.1)

    assert len(handler.all) == number_of_items

    thread.join()

def test_reload_serial_number():
    """
    Проверяем, что при перезагрузке движка порядковый номер инкрементируется.
    """
    engine = Engine()
    store = SettingsStore()
    store['pool_size'] = 2
    engine.write({'lol': 'kek'})

    number_before = engine.serial_number
    engine.reload()
    number_after = engine.serial_number

    assert number_after == number_before + 1

def test_active_flag():
    """
    Проверяем, что флаг активности движка работает корректно.
    """
    engine = Engine()
    store = SettingsStore()
    store['pool_size'] = 2
    engine.write({'lol': 'kek'})

    engine.stop()
    assert engine.active == False

    engine.load()
    assert engine.active == True

    engine.reload()
    assert engine.active == True

    class NotSingleton:
        def __new__(cls):
            return object.__new__(cls)
    class TestEngine(NotSingleton, Engine):
        pass
    test_engine = TestEngine()

    assert test_engine.active == False

def test_load():
    """
    Проверяем, что после загрузки движка объект real_engine заменяется новым.
    """
    engine = Engine()
    store = SettingsStore()
    store['pool_size'] = 2
    engine.write({'lol': 'kek'})

    engine.stop()

    stopped_real_engine = engine.real_engine

    engine.load()

    assert not (stopped_real_engine is engine.real_engine)

def test_reload():
    """
    Проверяем, что после перезагрузки движка объект real_engine заменяется новым.
    """
    engine = Engine()
    store = SettingsStore()
    store['pool_size'] = 2
    engine.write({'lol': 'kek'})

    old_real_engine = engine.real_engine

    engine.reload()

    assert not (old_real_engine is engine.real_engine)

def for_process(path_to_logs_file, path_to_numbers_file, number_of_iterations):
    """
    Функция, предназначенная для выполнения в другом процессе.
    Через функцию log создается много логов, они все отправляются в многопоточный движок.
    К моменту завершения процесса все логи еще не должны успеть обработаться. Для проверки этого факта в конце работы процеса записывается длина очереди (она не должна быть нулевой, это потом булет проверено в тесте; если она нулевая, это значило бы, что все логи таки успели обработаться в штатном порядке).
    """
    config.add_handlers(file_writer(path_to_logs_file))
    config.set(pool_size=2)

    for index in range(number_of_iterations):
        log('kek')

    queue_size = Engine().real_engine.queue_size()
    with open(path_to_numbers_file, 'w') as file:
        file.write(str(queue_size))

def test_finalize(number_of_strings_in_the_files, delete_files):
    """
    Проверяем, что при остановке интерпретатора записываются не успевшие записаться логи в многопоточном движке.
    Для этого запускаем polog в другом процессе.
    """
    path_to_logs_file = 'polog/tests/data/other_process.log'
    path_to_numbers_file = 'polog/tests/data/queue_size.log'
    number_of_iterations = 10000

    delete_files(path_to_logs_file, path_to_numbers_file)

    process = Process(target=for_process, args=(path_to_logs_file, path_to_numbers_file, number_of_iterations))
    process.start()
    process.join()

    with open(path_to_numbers_file, 'r') as file:
        queue_size = int(file.read())

    assert queue_size != 0

    assert number_of_strings_in_the_files(path_to_logs_file) == number_of_iterations

    delete_files(path_to_logs_file, path_to_numbers_file)
