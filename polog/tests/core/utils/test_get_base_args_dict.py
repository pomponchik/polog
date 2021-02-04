import pytest
from polog.core.utils.get_base_args_dict import get_base_args_dict


def test_base():
    """
    Проверяем извлечение базовой информации из функции.
    """
    args = get_base_args_dict(test_base, 'kek')
    assert args['auto'] == True
    assert args['message'] == 'kek'
    assert args['function'] == test_base.__name__
    assert args['module'] == test_base.__module__
