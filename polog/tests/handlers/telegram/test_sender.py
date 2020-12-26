import time
import pytest
from polog.handlers.telegram.sender import TelegramSender
from polog import log, config
import sys
from my_config import MY_TOKEN, MY_CHAT

lst = []

config.add_handlers(TelegramSender(MY_TOKEN, MY_CHAT))


def test_send_normal():
    log('hello')
    time.sleep(0.0001)
