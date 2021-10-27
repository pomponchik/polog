import os

import pytest

from polog import log, config
from polog.handlers.file.rotation.rotator import Rotator
from polog.handlers.file.writer import file_writer
from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper


@pytest.mark.parametrize('size_limit,message,iterations', [
    ('3 megabytes', 'kek' * 1024, 1024),
    ('3 kilobytes', 'kek', 1024),
    ('3 megabyte', 'kek' * 1024, 1024),
    ('3 kilobyte', 'kek', 1024),
    ('3 mb', 'kek' * 1024, 1024),
    ('3 kb', 'kek', 1024),
    ('1 b', 'k', 1),
])
def test_base_behavior_rotation_file_size(size_limit, message, iterations, number_of_strings_in_the_files, delete_files, dirname_for_test, filename_for_test):
    """
    Проверяем, что ротация работает с набором валидных правил.

    Рабочая ротация означает, что:
    1. Когда надо - файл с ротированными логами создается.
    2. Когда файл с ротированными логами создается, в нем ровно то количество строк, которое мы записывали в исходный файл.
    3. После ротации в исходном файле - 0 строк.
    """
    handler = file_writer(filename_for_test)
    config.add_handlers(handler)
    config.set(pool_size=0)

    for iteration in range(iterations):
        log(message)

    rotator = Rotator(f'{size_limit} >> {dirname_for_test}', FileDependencyWrapper([filename_for_test], lock_type='thread+file'))
    rotator.maybe_do()

    assert len(os.listdir(dirname_for_test)) == 1

    archive_file = os.listdir(dirname_for_test)[0]
    archive_file = os.path.join(dirname_for_test, archive_file)

    assert number_of_strings_in_the_files(archive_file) == iterations
    assert number_of_strings_in_the_files(filename_for_test) == 0

    config.delete_handlers(handler)

def test_wrong_rule_to_rotation():
    """
    Проверяем, что для неформатных правил ротации поднимается ValueError.
    """
    with pytest.raises(ValueError):
        rotator = Rotator(f'lol >> kek', FileDependencyWrapper(()))
