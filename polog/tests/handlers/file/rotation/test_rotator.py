import os
import platform

import pytest

from polog import log, config
from polog.handlers.file.rotation.rotator import Rotator
from polog.handlers.file.writer import file_writer
from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper


@pytest.mark.skipif('windows' in platform.system().lower(), reason="file locks don't work on windows")
def test_base_behavior_rotation_file_size(number_of_strings_in_the_files, delete_files, dirname_for_test, filename_for_test):
    """
    Проверяем, что ротация работает с набором валидных правил.

    Рабочая ротация означает, что:
    1. Когда надо - файл с ротированными логами создается.
    2. Когда файл с ротированными логами создается, в нем ровно то количество строк, которое мы записывали в исходный файл.
    3. После ротации в исходном файле - 0 строк.
    """
    variations = [
        ('3 megabytes', 'kek' * 1024, 1024),
        ('3 kilobytes', 'kek', 1024),
        ('3 megabyte', 'kek' * 1024, 1024),
        ('3 kilobyte', 'kek', 1024),
        ('3 mb', 'kek' * 1024, 1024),
        ('3 kb', 'kek', 1024),
        ('1 b', 'k', 1),
    ]
    for size_limit, message, iterations in variations:

        handler = file_writer(filename_for_test)
        dirname_for_test = os.path.join(dirname_for_test, 'rotation_dir')
        config.add_handlers(handler)
        config.set(pool_size=0)

        for iteration in range(iterations):
            log(message)

        rotator = Rotator(f'{size_limit} >> {dirname_for_test}', FileDependencyWrapper([filename_for_test], lock_type='thread+file'))
        rotator.maybe_do()

        assert len([x for x in os.listdir(dirname_for_test) if not x.endswith('.lock')]) == 1

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
        rotator = Rotator(f'lol >> kek', FileDependencyWrapper((), lock_type='thread+file'))

def test_wrong_number_of_rules_to_rotation():
    """
    Проверяем, что, при неправильном числе элементов в выражении, поднимается исключение. Должно быть 2: справа и слева от '>>'.
    """
    with pytest.raises(ValueError):
        rotator = Rotator(f'lol >>', FileDependencyWrapper((), lock_type='thread+file'))

    with pytest.raises(ValueError):
        rotator = Rotator(f'>>', FileDependencyWrapper((), lock_type='thread+file'))

    with pytest.raises(ValueError):
        rotator = Rotator(f' >> ', FileDependencyWrapper((), lock_type='thread+file'))

    with pytest.raises(ValueError):
        rotator = Rotator(f'3 kilobyte >> logs.log >> kek.log', FileDependencyWrapper((), lock_type='thread+file'))
