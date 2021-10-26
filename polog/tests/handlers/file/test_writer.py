import io
import os
import sys
import time
from threading import Thread, get_ident
from multiprocessing import Process

import pytest

from polog import log, config
from polog.handlers.file.writer import file_writer


def test_base_writer(number_of_strings_in_the_files, delete_files):
    """
    Базовый сценарий - запись логов в файл.

    Проверяем, что в файл вообще что-то записывается.
    """
    iterations = 5
    path = 'polog/tests/data/data.log'
    handler = file_writer(path)
    config.add_handlers(handler)
    config.set(pool_size=0)

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
    config.set(pool_size=0)

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

    time.sleep(1.5)

    files = [filename_for_test]

    for filename in os.listdir(dirname_for_test):
        files.append(os.path.join(dirname_for_test, filename))

    assert number_of_strings_in_the_files(*files) == expected_number_of_logs

    config.delete_handlers(handler)

def create_logs_for_process(process_index, number_of_logs, filename_for_test, dirname_for_test, timeout):
    config.set(pool_size=2, level=1)
    handler = file_writer(filename_for_test, rotation=f'3 kb >> {dirname_for_test}')
    config.add_handlers(handler)

    for index in range(number_of_logs):
        message = f'{process_index} {index}'
        log(message)

    time.sleep(timeout)

def test_multiprocessing_concurrent_write(number_of_strings_in_the_files, filename_for_test, dirname_for_test):
    """
    Запускаем много логов в нескольких процессах и проверяем, что они все успевают записаться в файл, и при этом в ничего не было потеряно при ротациях.
    """
    number_of_logs_per_process = 2000
    number_of_processes = 20
    timeout = 1.5

    processes = [Process(target=create_logs_for_process, args=(index, number_of_logs_per_process, filename_for_test, dirname_for_test, timeout)) for index in range(number_of_processes)]
    for process in processes:
        process.start()
    for process in processes:
        process.join()

    expected_number_of_logs = number_of_logs_per_process * number_of_processes

    files = [filename_for_test]

    for filename in os.listdir(dirname_for_test):
        files.append(os.path.join(dirname_for_test, filename))

    assert number_of_strings_in_the_files(*files) == expected_number_of_logs
