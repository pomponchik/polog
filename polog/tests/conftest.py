import os
import shutil
import uuid

import pytest
from termcolor import colored

from polog import config
from polog.core.stores.settings.settings_store import SettingsStore
from polog.handlers.memory.saver import memory_saver


@pytest.fixture
def handler():
    """
    Получаем стандартный обработчик, сохраняющий логи в оперативную память.
    """
    new_handler = memory_saver()
    new_handler.clean()
    try:
        config.add_handlers(new_handler)
    except ValueError as e:
        pass
    return new_handler

@pytest.fixture
def empty_class():
    """
    Заготовка класса.
    """
    class EmptyClass:
        pass
    return EmptyClass

@pytest.fixture
def settings_mock():
    """
    Подмена экземпляра класса настроек.
    """
    class SettingsMock:
        def __init__(self):
            self.points = {'started': True, 'pool_size': 2, 'max_delay_before_exit': 0.001, 'max_queue_size': 50, 'time_quant': 0.001, 'service_name': 'kek', 'delay_on_exit_loop_iteration_in_quants': 10}
            self.handlers = {}
            self.fields = {}
        def __getitem__(self, key):
            return self.points[key]
        def __setitem__(self, key, value):
            points[key] = value
        def force_get(self, key):
            return self.points[key]
    return SettingsMock()

@pytest.fixture
def delete_files():
    """
    Функция, удаляющая все файлы, пути к которым были переданы в качестве аргументов.
    """
    def result(*files):
        for file in files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass
            except PermissionError:
                os.rmdir(file)
    return result

@pytest.fixture
def number_of_strings_in_the_files():
    """
    Функция, подсчитывающая не пустые строки в файлах, пути к которым были переданы в качестве аргументов.
    """
    def result(*paths):
        result = 0
        for path in paths:
            try:
                with open(path, 'r') as file:
                    for line in file:
                        if line:
                            result += 1
            except FileNotFoundError:
                pass
            except IsADirectoryError:
                pass
        return result
    return result

@pytest.fixture
def filename_for_test(dirname_for_test):
    """
    Получаем имя файла в тестовой директории и удаляем за собой файл.
    """
    yield os.path.join(dirname_for_test, f'data_{uuid.uuid1().hex}.log')

@pytest.fixture
def dirname_for_test(delete_files):
    """
    Получаем имя файла в тестовой директории и удаляем за собой файл.
    """
    path = f'polog/tests/data/'
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path)
    yield path
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path)
    open(os.path.join(path, '.gitkeep'), 'w').close()

@pytest.hookimpl
def pytest_runtest_makereport(item, call):
    """
    Хук, добавляющий информацию о текущих настройках к каждому выводу об ошибке в тесте.
    """
    if call.when == 'call':
        if call.excinfo:
            item.add_report_section("call", "config", colored(str(SettingsStore()), 'cyan'))
