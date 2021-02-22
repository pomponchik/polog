import json
import pytest
from polog.core.utils.log_normal_info import log_normal_info
from polog.utils.json_vars import json_one_variable


def test_base_info():
    """
    Проверяем, что базовая информация извлекается.
    """
    data = {}
    log_normal_info('kek', 1.0, 0.5, data, 7)
    assert data.get('exception_type') is None
    assert data.get('exception_message') is None
    assert data['time_of_work'] == 0.5
    assert data['level'] == 7
    assert data['success'] == True
    assert data.get('traceback') is None
    assert data.get('local_variables') is None
    assert data.get('message') is None
    assert data.get('input_variables') is None
    assert data.get('function') is None
    assert data.get('module') is None
    assert data.get('result') == json_one_variable('kek')
