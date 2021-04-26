import pytest
from polog.core.utils.not_none_to_dict import not_none_to_dict


def test_base():
    """
    Проверяем, что None в словаре не сохраняется, прочие значения - сохраняются.
    """
    data = {}
    not_none_to_dict(data, 'key', 'value')
    assert data['key'] == 'value'
    data = {}
    not_none_to_dict(data, 'key', None)
    assert data.get('key') is None
