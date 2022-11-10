from threading import Thread

import pytest

from polog.handlers.file.locks.thread_lock import ThreadLock


def test_threads_race_condition():
    """
    Проверяем, что если лок включен - он работает.
    """
    iterations = 500000
    number_of_threads = 4
    lock = ThreadLock(on=True)

    index = 0
    def incrementer(iterations):
        nonlocal index
        for _ in range(iterations):
            lock.acquire()
            index += 1
            lock.release()

    threads = [Thread(target=incrementer, args=(iterations, )) for thread_index in range(number_of_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert index == iterations * number_of_threads


def test_threads_race_condition_lock_off():
    """
    Проверяем, что если лок выключен - он не работает.
    Из-за состояния гонки инкремент должен "пробуксовывать".
    """
    iterations = 500000
    number_of_threads = 4
    lock = ThreadLock(on=False)

    index = 0
    def incrementer(iterations):
        nonlocal index
        for _ in range(iterations):
            lock.acquire()
            index += 1
            lock.release()

    threads = [Thread(target=incrementer, args=(iterations, )) for thread_index in range(number_of_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert index < iterations * number_of_threads

def test_threads_race_condition_without_locks():
    """
    Проверяем, что состояние гонки возникает без использования локов.
    """
    iterations = 500000
    number_of_threads = 4

    index = 0
    def incrementer(iterations):
        nonlocal index
        for _ in range(iterations):
            index += 1

    threads = [Thread(target=incrementer, args=(iterations, )) for thread_index in range(number_of_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert index < iterations * number_of_threads
