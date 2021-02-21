from threading import Thread
import pytest
from polog.core.utils.read_only_singleton import ReadOnlySingleton


def test_singleton():
    """
    Проверяем, что объект отнаследованного от ReadOnlySingleton класса всегда один.
    """
    class ExampleSingleton(ReadOnlySingleton):
        pass
    assert ExampleSingleton() is ExampleSingleton()

def test_stress():
    """
    Проверка блокировки создания объекта.

    Несколько потоков одновременно генерируют объекты класса, отнаследованного от ReadOnlySingleton.
    Проверяем, что они всегда создают один и тот же объект.
    """
    class ExampleSingleton(ReadOnlySingleton):
        pass
    ids = set()
    def target():
        for index in range(1000):
            ids.add(id(ExampleSingleton()))
    treads = []
    for number in range(5):
        tread = Thread(target=target)
        tread.daemon = True
        treads.append(tread)
        tread.start()
    for thread in treads:
        tread.join()
    assert len(ids) == 1
