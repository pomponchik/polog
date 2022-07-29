import io
import os
import sys
import time
import asyncio
from threading import Thread, get_ident
from multiprocessing import Process

import pytest

from polog import log, config
from polog.handlers.file.writer import file_writer

TIMEOUT = 3


def test_base_writer(number_of_strings_in_the_files, delete_files):
    """
    Базовый сценарий - запись логов в файл.

    Проверяем, что в файл вообще что-то записывается.
    """
    iterations = 5
    path = 'polog/tests/data/data.log'
    handler = file_writer(path)
    config.add_handlers(handler)
    config.set(pool_size=0, level=0)

    for iteration in range(iterations):
        log('kek')

    assert number_of_strings_in_the_files(path) == iterations

    config.delete_handlers(handler)
    delete_files(path)

def test_output_to_console_is_working_without_path_argument():
    """
    Проверяем, что если в файловый обработчик не передать параметров, он будет выводить логи в stdout.
    """
    stdout = sys.stdout
    instead_of_file = io.StringIO()
    sys.stdout = instead_of_file
    handler = file_writer()
    config.add_handlers(handler)
    config.set(pool_size=0, level=0)

    log('kek')

    log_string = instead_of_file.getvalue()
    assert log_string

    config.delete_handlers(handler)
    sys.stdout = stdout

def test_error_if_two_parameters():
    """
    Проверяем, что если параметров слишком много - поднимется исключение.
    """
    with pytest.raises(ValueError):
        file_writer('a', 'b')

def test_parameter_is_not_string_and_not_file_object(delete_files):
    """
    Проверяем, что валидным неименованным параметром принимаются только файловые объекты и строки, при других вариантах - поднимаются исключения.
    """
    file_writer(io.StringIO())
    path = 'polog/tests/data/data.log'
    file_writer(path)
    with pytest.raises(ValueError):
        file_writer(777)
    delete_files(path)

def test_base_concurrent_write(number_of_strings_in_the_files, filename_for_test, dirname_for_test):
    """
    Запускаем много логов в нескольких потоках и проверяем, что они все успевают записаться в файл, и при этом в ничего не было потеряно при ротациях.
    """
    number_of_logs_per_thread = 2000
    number_of_threads = 20

    config.set(pool_size=20, level=1)

    handler = file_writer(filename_for_test, rotation=f'3 kb >> {dirname_for_test}')
    config.add_handlers(handler)

    def create_a_lot_of_logs(number_of_logs):
        thread_name = get_ident()
        for index in range(number_of_logs):
            message = f'{thread_name} {index}'
            log(message)

    threads = [Thread(target=create_a_lot_of_logs, args=(number_of_logs_per_thread,)) for x in range(number_of_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    expected_number_of_logs = number_of_logs_per_thread * number_of_threads

    time.sleep(TIMEOUT)

    files = []

    for filename in os.listdir(dirname_for_test):
        files.append(os.path.join(dirname_for_test, filename))

    assert number_of_strings_in_the_files(*files) == expected_number_of_logs

    config.delete_handlers(handler)

def create_logs_for_process(process_index, number_of_logs, filename_for_test, dirname_for_test):
    """
    Функция предназначена для запуска в отдельном процессе.

    Она записывает в файл filename_for_test number_of_logs строчек лога.
    """
    config.set(pool_size=2, level=1)
    handler = file_writer(filename_for_test, rotation=f'3 kb >> {dirname_for_test}', lock_type='file+thread')
    config.add_handlers(handler)

    for index in range(number_of_logs):
        message = f'{process_index} {index}'
        log(message)

    time.sleep(TIMEOUT)

def test_multiprocessing_concurrent_write(number_of_strings_in_the_files, filename_for_test, dirname_for_test):
    """
    Запускаем много логов в нескольких процессах и проверяем, что они все успевают записаться в файл, и при этом в ничего не было потеряно при ротациях.
    """
    number_of_logs_per_process = 2000
    number_of_processes = 20

    processes = [Process(target=create_logs_for_process, args=(index, number_of_logs_per_process, filename_for_test, dirname_for_test)) for index in range(number_of_processes)]
    for process in processes:
        process.start()
    for process in processes:
        process.join()

    expected_number_of_logs = number_of_logs_per_process * number_of_processes

    files = []

    for filename in os.listdir(dirname_for_test):
        files.append(os.path.join(dirname_for_test, filename))

    assert number_of_strings_in_the_files(*files) == expected_number_of_logs

def test_alt_function_for_file_writer(filename_for_test, number_of_strings_in_the_files, handler):
    """
    Проверяем, что вызов альтернативной функции работает корректно.

    Это должно происходить в двух случаях:
    1. В случае, если запись лога запрещена фильтрами.
    2. Если лог записать по какой-то причине не удалось (то есть в процессе записи поднялось любое исключение).
    """
    file_handler = file_writer(filename_for_test, only_errors=True, alt=handler)
    config.set(pool_size=0, level=1)
    config.delete_handlers(handler)
    config.add_handlers(file_handler)
    handler.clean()

    log('kek')
    assert handler.last is not None
    handler.clean()

    log('kek', success=True)
    assert handler.last is not None
    handler.clean()

    log('kek', success=False)
    assert handler.last is None
    handler.clean()

    config.delete_handlers(file_handler)

    class FakeFileWrapper:
        def __init__(self, file, lock_type):
            pass
        def write(self, data):
            raise ValueError

    file_handler = file_writer(filename_for_test, alt=handler, file_wrapper=FakeFileWrapper)
    config.add_handlers(file_handler)

    log('kek')
    assert handler.last is not None
    handler.clean()

    config.delete_handlers(file_handler)

    file_handler = file_writer(filename_for_test, alt=handler)
    config.add_handlers(file_handler)

    log('kek')
    assert handler.last is None

    handler.clean()

def test_filter_function_for_file_handler(filename_for_test, number_of_strings_in_the_files):
    """
    Проверяем, что фильтр работает.
    """
    file_handler = file_writer(filename_for_test, filter=lambda x: True)
    config.add_handlers(file_handler)
    config.set(pool_size=0, level=1)

    log('kek')

    assert number_of_strings_in_the_files(filename_for_test) == 1

    config.delete_handlers(file_handler)
    file_handler = file_writer(filename_for_test, filter=lambda x: False)
    config.add_handlers(file_handler)

    log('kek')

    assert number_of_strings_in_the_files(filename_for_test) == 1

def test_only_errors_for_file_handler(filename_for_test, number_of_strings_in_the_files):
    """
    Проверяем, что базовый фильтр, отсекающий не-ошибки, работает.
    """
    file_handler = file_writer(filename_for_test, only_errors=True)
    config.add_handlers(file_handler)
    config.set(pool_size=0, level=1)

    log('kek')

    assert number_of_strings_in_the_files(filename_for_test) == 0

    log('kek', success=False)

    assert number_of_strings_in_the_files(filename_for_test) == 1

    config.delete_handlers(file_handler)
    file_handler = file_writer(filename_for_test, only_errors=False)
    config.add_handlers(file_handler)

    log('kek')

    assert number_of_strings_in_the_files(filename_for_test) == 2

    log('kek', success=False)

    assert number_of_strings_in_the_files(filename_for_test) == 3

def test_check_chunks_output(filename_for_test):
    """
    Проверяем, что вывод содержит некоторые ожидаемые кусочки.
    """
    file_handler = file_writer(filename_for_test)
    config.add_handlers(kek=file_handler)
    config.set(pool_size=0, level=1)

    log('kek', level=10)

    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]

    assert 'MANUAL' in string
    assert '"kek"' in string
    assert 'UNKNOWN' in string

    log('kek', level=10, success=True)

    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]

    assert 'SUCCESS' in string

    log('kek', level=10, success=False)

    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]

    assert 'ERROR' in string

    config.delete_handlers('kek')

def test_check_full_string(handler, filename_for_test):
    """
    По сути сквозной тест.
    Проверяем, что строка лога, выведенного в файл, полностью соответствует шаблону.
    """
    file_handler = file_writer(filename_for_test)
    config.add_handlers(kek=file_handler)
    config.set(pool_size=0, level=1, service_name='base')
    config.levels(test_check_full_string_level=10)
    config.delete_engine_fields(*(config.get_engine_fields().keys()))
    config.delete_fields(*(config.get_in_place_fields().keys()))

    log('kek', level='test_check_full_string_level', success=True)
    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]
    assert string == f'[{handler.last["time"]}] | test_check_full_string_level | SUCCESS | MANUAL | "kek" | where: base.?'

    log('kek', level='test_check_full_string_level', success=False)
    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]
    assert string == f'[{handler.last["time"]}] | test_check_full_string_level |  ERROR  | MANUAL | "kek" | where: base.?'

    log('kek', level='test_check_full_string_level')
    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]
    assert string == f'[{handler.last["time"]}] | test_check_full_string_level | UNKNOWN | MANUAL | "kek" | where: base.?'

    log('kek', level='test_check_full_string_level', lol=10)
    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]
    assert string == f'[{handler.last["time"]}] | test_check_full_string_level | UNKNOWN | MANUAL | "kek" | where: base.? | lol: 10'

    log('kek', level='test_check_full_string_level', lol="kek")
    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]
    assert string == f'[{handler.last["time"]}] | test_check_full_string_level | UNKNOWN | MANUAL | "kek" | where: base.? | lol: "kek"'

    @log(message='kek', level='test_check_full_string_level')
    def function(a, b, c):
        return a + b + c
    function(1, 2, 3)
    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]
    time_of_work = f'{handler.last["time_of_work"]:.8f}'
    time_of_work = time_of_work.rstrip('0.')
    assert string == f'[{handler.last["time"]}] | test_check_full_string_level | SUCCESS |  AUTO  | "kek" | where: base.file.test_writer.function() | time of work: {time_of_work} sec. | input variables: 1 (int), 2 (int), 3 (int) | result: 6 (int)'

    class Kek:
        @log(message='kek', level='test_check_full_string_level')
        def method(self, a, b, c):
            return a + b + c
    Kek().method(1, 2, 3)
    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]
    time_of_work = f'{handler.last["time_of_work"]:.8f}'
    time_of_work = time_of_work.rstrip('0.')
    assert string.startswith(f'[{handler.last["time"]}] | test_check_full_string_level | SUCCESS |  AUTO  | "kek" | where: base.file.test_writer.Kek.method() | time of work: {time_of_work} sec. | input variables: ')
    assert string.endswith(f'1 (int), 2 (int), 3 (int) | result: 6 (int)')

    @log(message='kek', level='test_check_full_string_level')
    class Kek:
        def method(self, a, b, c):
            return a + b + c
    Kek().method(1, 2, 3)
    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]
    time_of_work = f'{handler.last["time_of_work"]:.8f}'
    time_of_work = time_of_work.rstrip('0.')
    assert string.startswith(f'[{handler.last["time"]}] | test_check_full_string_level | SUCCESS |  AUTO  | "kek" | where: base.file.test_writer.Kek.method() | time of work: {time_of_work} sec. | input variables: ')
    assert string.endswith(f'1 (int), 2 (int), 3 (int) | result: 6 (int)')

    @log(message='kek', level='test_check_full_string_level')
    class Kek:
        async def method(self, a, b, c):
            return a + b + c
    asyncio.run(Kek().method(1, 2, 3))
    with open(filename_for_test, 'r') as file:
        string = [string for string in file.read().split('\n') if string][-1]
        print(string)
    time_of_work = f'{handler.last["time_of_work"]:.8f}'
    time_of_work = time_of_work.rstrip('0.')
    assert string.startswith(f'[{handler.last["time"]}] | test_check_full_string_level | SUCCESS |  AUTO  | "kek" | where: base.file.test_writer.Kek.method() | time of work: {time_of_work} sec. | input variables: ')
    assert string.endswith(f'1 (int), 2 (int), 3 (int) | result: 6 (int)')

    config.delete_handlers('kek')
