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
