import pytest
from polog.core.utils.log_exception_info import log_exception_info


def test_base_info():
    """
    Проверяем, что базовая информация об исключении извлекается.
    """
    data = {}
    try:
        raise ValueError('lol')
    except Exception as e:
        log_exception_info(e, 1.0, 0.5, data, 7)
    assert data['exception_type'] == 'ValueError'
    assert data['exception_message'] == 'lol'
    assert data['time_of_work'] == 0.5
    assert data['level'] == 7
    assert data['success'] == False
    assert len(data['traceback']) > 0
    assert len(data['local_variables']) > 0
    assert data.get('message') is None
    assert data.get('input_variables') is None
    assert data.get('function') is None
    assert data.get('module') is None
    assert data.get('result') is None
