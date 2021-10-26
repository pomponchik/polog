import os

import pytest

from polog import log, config
from polog.handlers.file.rotation.rotator import Rotator
from polog.handlers.file.writer import file_writer
from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper


@pytest.mark.parametrize('size_limit,message,iterations,expected', [
    ('3 megabytes', 'kek' * 1024, 1024, True),
    ('100 megabytes', 'kek' * 1024, 1024, False),
    ('3 kilobytes', 'kek', 1024, True),
    ('100 kilobytes', 'kek', 1024, False),
    ('3 megabyte', 'kek' * 1024, 1024, True),
    ('100 megabyte', 'kek' * 1024, 1024, False),
    ('3 kilobyte', 'kek', 1024, True),
    ('100 kilobyte', 'kek', 1024, False),
    ('3 mb', 'kek' * 1024, 1024, True),
    ('100 mb', 'kek' * 1024, 1024, False),
    ('3 kb', 'kek', 1024, True),
    ('100 kb', 'kek', 1024, False),
    ('1 b', 'k', 1, True),
])
def test_base_behavior_rotation_file_size(size_limit, message, iterations, expected, number_of_strings_in_the_file, delete_files):
    """
    Проверяем, что ротация работает с набором валидных правил.

    Рабочая ротация означает, что:
    1. Когда надо - файл с ротированными логами создается.
    2. Когда файл с ротированными логами создается, в нем ровно то количество строк, которое мы записывали в исходный файл.
    3. После ротации в исходном файле - 0 строк.
    """
    path = 'polog/tests/data/data.log'
    archive_path = 'polog/tests/data/archive'
    handler = file_writer(path)
    config.add_handlers(handler)
    config.set(pool_size=0)
    to_delete = [path]

    for iteration in range(iterations):
        log(message)

    rotator = Rotator(f'{size_limit} >> {archive_path}', FileDependencyWrapper([path]))
    rotator.maybe_do()

    if expected:
        assert len(os.listdir(archive_path)) == 1

        archive_file = os.listdir(archive_path)[0]
        archive_file = os.path.join(archive_path, archive_file)

        assert number_of_strings_in_the_file(archive_file) == iterations
        assert number_of_strings_in_the_file(path) == 0

        to_delete.append(archive_file)
        to_delete.append(archive_path)
    else:
        assert not os.path.exists(archive_path)

    config.delete_handlers(handler)
    delete_files(*to_delete)

def test_wrong_rule_to_rotation():
    """
    Проверяем, что для неформатных правил ротации поднимается ValueError.
    """
    with pytest.raises(ValueError):
        rotator = Rotator(f'lol >> kek', FileDependencyWrapper(()))
