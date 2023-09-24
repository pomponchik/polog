import pytest

from polog.core.utils.exception_to_dict import exception_to_dict


def test_exception_to_dict():
    """
    Проверяем, что из исключения в словарь извлекаются его название и сообщение.
    """
    args = {}
    try:
        raise Exception('hi!')
    except Exception as e:
        exception_to_dict(args, e)
    assert args['exception_message'] == 'hi!'
    assert args['exception_type'] == 'Exception'
