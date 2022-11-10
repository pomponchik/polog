from multiprocessing import Process, current_process
from threading import Thread
import shutil
import os

import pytest

from polog.handlers.file.locks.file_lock import FileLock


def process_race_condition_generator(filename, number_of_iterations, number_of_process):
    lock = FileLock(filename)
    file = open(filename, 'a', encoding='utf-8')
    for index in range(number_of_iterations):
        lock.acquire()
        file.write('abc\n')
        if index % 10:
            new_path = f'{filename}_{current_process()}_{index}.log'
            shutil.move(filename, new_path)
            file.close()
            file = open(filename, 'a', encoding='utf-8')
        lock.release()

def test_file_lock_race_condition_in_processes(filename_for_test, number_of_strings_in_the_files, delete_files, dirname_for_test):
    """
    Провоцируем состояние гонки между процессами.
    """
    number_of_processes = 5
    number_of_iterations = 200

    processes = [Process(target=process_race_condition_generator, args=(filename_for_test, number_of_iterations, index)) for index in range(number_of_processes)]

    for process in processes:
        process.start()
    for process in processes:
        process.join()

    files = [filename_for_test]

    expected_number_of_logs = number_of_processes * number_of_iterations


    for filename in os.listdir(os.path.join('polog', 'tests', 'data')):
        if not filename.startswith('.') and not os.path.isdir(filename):
            files.append(os.path.join('polog', 'tests', 'data', filename))

    assert number_of_strings_in_the_files(*files) == expected_number_of_logs
    delete_files(*[os.path.join('polog', 'tests', 'data', filename) for filename in os.listdir(os.path.join('polog', 'tests', 'data')) if not os.path.isdir(filename) and not filename == '.gitkeep'])

def test_active_flag_is_working_for_file_lock(filename_for_test):
    """
    Проверяем, что атрибут .active проставляется правильно.
    """
    assert FileLock(filename_for_test).active == True
    assert FileLock(None).active == False

def test_file_lock_race_condition_in_threads(filename_for_test):
    """
    Проверяем, что файловый лок работает и на тредах.
    """
    number_of_threads = 10
    number_of_iterations = 10000

    lock = FileLock(filename_for_test)
    counter = 0

    def increment(number_of_iterations):
        nonlocal counter

        for _ in range(number_of_iterations):
            lock.acquire()
            counter += 1
            lock.release()

    threads = [Thread(target=increment, args=(number_of_iterations, )) for _ in range(number_of_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert counter == number_of_threads * number_of_iterations
