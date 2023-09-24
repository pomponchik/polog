import json

import pytest

from polog.core.utils.is_json import is_json


def test_recognize_valid_json():
    """
    Валидные строки json-формата должны распознаваться как таковые. Проверяем.
    """
    assert is_json(json.dumps({'lol': 'kek'}))

def test_recognize_not_valid_json():
    """
    Невалидные в рамках json-формата строки тоже должны распознаваться как таковые. Проверяем.
    """
    assert not is_json('{')
    assert not is_json(']')
    assert not is_json(json.dumps({'lol': 'kek'})[:-1])
    assert not is_json(1)
    assert not is_json('kek')
