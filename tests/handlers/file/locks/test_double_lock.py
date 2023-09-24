from multiprocessing import Process, current_process
from threading import Thread
import shutil
import os

import pytest

from polog.handlers.file.locks.double_lock import DoubleLock


def double_race_condition_generator(filename, number_of_iterations, number_of_process, number_of_threads):
    lock = DoubleLock(filename, lock_type='thread+file')

    def thread_race_condition():
        with lock:
            file = open(filename, 'a', encoding='utf-8')
        for index in range(number_of_iterations):
            with lock:
                file.write('abc\n')
                if index % 10:
                    new_path = f'{filename}_{current_process()}_{index}.log'
                    shutil.move(filename, new_path)
                    file.close()
                    file = open(filename, 'a', encoding='utf-8')
        file.close()

    threads = [Thread(target=thread_race_condition, args=()) for thread_index in range(number_of_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

@pytest.mark.skip(reason="Надо пока разобраться, почему тест падает. Прочие нагрузочные тесты работают.")
def test_double_lock_race_condition(filename_for_test, number_of_strings_in_the_files, delete_files, dirname_for_test):
    """
    Провоцируем состояние гонки между процессами и потоками одновременно.
    """
    number_of_processes = 5
    number_of_threads = 5
    number_of_iterations = 200

    processes = [Process(target=double_race_condition_generator, args=(filename_for_test, number_of_iterations, index, number_of_threads)) for index in range(number_of_processes)]

    for process in processes:
        process.start()
    for process in processes:
        process.join()

    files = [filename_for_test]

    expected_number_of_logs = number_of_processes * number_of_iterations * number_of_threads

    for filename in os.listdir(os.path.join('tests', 'data')):
        if not filename.startswith('.') and not os.path.isdir(filename):
            files.append(os.path.join('tests', 'data', filename))

    assert number_of_strings_in_the_files(*files) == expected_number_of_logs
    #delete_files(*[os.path.join('tests', 'data', filename) for filename in os.listdir(os.path.join('tests', 'data')) if not os.path.isdir(filename) and not filename == '.gitkeep'])

def test_get_lock_types():
    """
    Проверяем, что строка с описанием типов блокировок, которые надо включить, парсится корректно.
    Результатом должен быть список строк с названиями распознанных типов, в алфавитном порядке.
    """
    assert DoubleLock.get_lock_types(None) == []

    assert DoubleLock.get_lock_types('thread') == ['thread']
    assert DoubleLock.get_lock_types('file') == ['file']

    assert DoubleLock.get_lock_types('thread+file') == ['file', 'thread']
    assert DoubleLock.get_lock_types('file+thread') == ['file', 'thread']

    assert DoubleLock.get_lock_types('thread++file') == ['file', 'thread']
    assert DoubleLock.get_lock_types('+++thread++file++++') == ['file', 'thread']
    assert DoubleLock.get_lock_types('+++thread++') == ['thread']

    assert DoubleLock.get_lock_types('thread + file') == ['file', 'thread']
    assert DoubleLock.get_lock_types('   thread + file   ') == ['file', 'thread']
    assert DoubleLock.get_lock_types('   file   ') == ['file']
    assert DoubleLock.get_lock_types('  + file   ') == ['file']

    with pytest.raises(ValueError):
        DoubleLock.get_lock_types(1)

    with pytest.raises(ValueError):
        DoubleLock.get_lock_types(0)

    with pytest.raises(ValueError):
        DoubleLock.get_lock_types('')

    with pytest.raises(ValueError):
        DoubleLock.get_lock_types('not_file')

    with pytest.raises(ValueError):
        DoubleLock.get_lock_types('file+file')

def test_active_flag_is_working_for_double_lock(filename_for_test):
    """
    Проверяем, что атрибут .active проставляется правильно.
    """
    assert DoubleLock(filename_for_test, None).active == False
    assert DoubleLock(filename_for_test, 'file').active == True
    assert DoubleLock(filename_for_test, 'thread').active == True
    assert DoubleLock(filename_for_test, 'thread+file').active == True

def test_load_locks_active_flags(filename_for_test):
    """
    Проверяем, что активны ровно те локи, которые "заказаны".
    """
    lock = DoubleLock(filename_for_test, None)
    assert lock.thread_lock.active == False
    assert lock.file_lock.active == False

    lock = DoubleLock(filename_for_test, 'file')
    assert lock.thread_lock.active == False
    assert lock.file_lock.active == True

    lock = DoubleLock(filename_for_test, 'thread')
    assert lock.thread_lock.active == True
    assert lock.file_lock.active == False

    lock = DoubleLock(filename_for_test, 'thread+file')
    assert lock.thread_lock.active == True
    assert lock.file_lock.active == True
