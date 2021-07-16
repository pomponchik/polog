import pytest
from polog.core.engine.engine import Engine


def test_singleton():
    """
    Проверяем, что Writer - это синглтон.
    """
    assert Engine() is Engine()
