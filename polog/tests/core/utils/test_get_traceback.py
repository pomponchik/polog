import time
import json
import pytest
from polog.core.utils.get_traceback import get_traceback, get_locals_from_traceback
from polog import json_vars, config


non_local = []

def test_locals_full():
    """
    Проверяем, что локальные переменные из исключения извлекаются и представлены в стандартной схеме json.
    """
    a = 5
    b = 'lol'
    try:
        c = 5 / 0
    except:
        non_local.append(get_locals_from_traceback())
        non_local.append(json_vars(**locals()))
        assert non_local[0] == non_local[1]
        non_local.pop()
        non_local.pop()

def test_get_traceback():
    """
    Проверяем, что извлеченный трейсбэк не пустой, то есть содержит хотя бы 1 символ.
    Содержимое трейсбэка здесь не проверяется.
    """
    a = 5
    b = 'lol'
    try:
        c = 5 / 0
    except:
        assert len(get_traceback())

def test_get_traceback_json_format():
    """
    Проверяем, что извлеченный трейсбэк корректно декодируется из формата json, то есть изначально в нем представлен.
    """
    a = 5
    b = 'lol'
    try:
        c = 5 / 0
    except:
        try:
            trace = get_traceback()
            trace = json.loads(trace)
            assert True
        except:
            assert False
