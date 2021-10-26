import io
import sys
import time

import pytest

from polog import log, config
from polog.handlers.file.writer import file_writer


def test_base_writer(number_of_strings_in_the_file, delete_files):
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

    assert number_of_strings_in_the_file(path) == iterations

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
