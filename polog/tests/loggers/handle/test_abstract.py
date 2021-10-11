import time

import pytest

from polog.loggers.handle.abstract import AbstractHandleLogger
from polog import config


class HandleLogger(AbstractHandleLogger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs_store = []

    def _push(self, fields):
        self.logs_store.append({**fields})

    def _specific_processing(self, fields):
        fields['lol'] = 'kek'


def test_inherit_is_working():
    """
    Проверяем, что у отнаследованного от базового класса класса работает базовый механизм.
    А именно, что вызывается сначала ._specific_processing(), затем ._push(), которые были переопределены у наследника.
    """
    logger = HandleLogger()
    logger('kek')
    time.sleep(0.0001)
    log = logger.logs_store[0]
    assert log['message'] == 'kek'
    assert log['lol'] == 'kek'

def test_hidden_fields():
    """
    Проверяем, что у ручного логгера нет ни одного поля, не начинающегося на "_" (за исключением того, что мы сами определили уже в наследнике базового класса).
    """
    logger = HandleLogger()
    for name in dir(logger):
        if name != 'logs_store':
            assert name.startswith('_')

def test_maybe_raise():
    """
    Проверяем, что внутренние исключения поднимаются в зависимости от установленных настроек.
    """
    config.set(silent_internal_exceptions=False)
    with pytest.raises(ValueError):
        HandleLogger._maybe_raise(ValueError, 'kek')
    config.set(silent_internal_exceptions=True)
    HandleLogger._maybe_raise(ValueError, 'kek')
