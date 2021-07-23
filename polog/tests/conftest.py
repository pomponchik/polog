import pytest
from polog import config
from polog.handlers.memory.saver import memory_saver


@pytest.fixture
def handler():
    """
    Получаем стандартный обработчик, сохраняющий логи в оперативную память.
    """
    new_handler = memory_saver()
    try:
        config.add_handlers(new_handler)
    except ValueError:
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
            self.points = {'started': True, 'pool_size': 2, 'delay_before_exit': 0.1, 'max_queue_size': 50, 'time_quant': 0.001, 'service_name': 'kek'}
            self.handlers = {}
            self.fields = {}
        def __getitem__(self, key):
            return self.points[key]
        def __setitem__(self, key, value):
            points[key] = value
        def force_get(self, key):
            return self.points[key]
    return SettingsMock()
