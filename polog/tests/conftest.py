import pytest
from polog import config
from polog.handlers.memory.saver import memory_saver


@pytest.fixture
def handler():
    new_handler = memory_saver()
    config.add_handlers(new_handler)
    return new_handler

@pytest.fixture
def empty_class():
    class EmptyClass:
        pass
    return EmptyClass
