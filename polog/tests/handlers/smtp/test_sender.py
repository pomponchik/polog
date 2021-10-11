import time

import pytest

from polog.handlers.smtp.sender import SMTP_sender
from polog import handle_log as log, config


lst = []

class DependencyWrapper:
    def __init__(self, v1, v2, v3, v4, v5):
        pass

    def send(self, message):
        lst.append(message)

sender = SMTP_sender('fff', 'fff', 'fff', 'fff', smtp_wrapper=DependencyWrapper)


def test_send_normal():
    """
    Проверяем, что что-то проходит через обработчик в DependencyWrapper.
    """
    config.add_handlers(sender)

    log('hello')
    time.sleep(0.0001)
    assert lst[0]
    lst.pop()

    config.delete_handlers(sender)

def test_send_error():
    """
    Проверка, что при исключении тоже что-то приходит в обработчик.
    """
    config.add_handlers(sender)

    log('hello', exception=ValueError())
    time.sleep(0.0001)
    assert lst[0]
    lst.pop()

    config.delete_handlers(sender)

def test_repr():
    """
    Проверяем, что метод .__repr__ обработчика подчиняется заданному формату отображения.
    """
    assert repr(sender) == 'SMTP_sender(email_from="fff", password=<HIDDEN>, smtp_server="fff", email_to="fff", port=465, text_assembler=None, subject_assembler=None, alt=None)'
