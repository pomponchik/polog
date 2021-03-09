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
