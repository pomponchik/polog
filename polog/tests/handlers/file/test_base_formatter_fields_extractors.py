import datetime
import pytest
from polog.handlers.file.base_formatter_fields_extractors import BaseFormatterFieldsExtractors as Extractors
from polog import config, json_vars
from polog.core.base_settings import BaseSettings


def test_full_time():
    tag = datetime.datetime(2021, 2, 7, 23, 46)
    tag_string = '[2021-02-07 23:46:00]'
    assert Extractors.time(**{'time': tag}) == tag_string

def test_empty_time():
    assert Extractors.time(**{}) is None

def test_full_level():
    assert Extractors.level(**{'level': 123}) == '123'
    config.levels(SOMELEVEL=123)
    assert Extractors.level(**{'level': 123}) == 'SOMELEVEL'

def test_empty_level():
    assert Extractors.level(**{}) is None

def test_full_message():
    assert Extractors.message(**{'message': 'lol'}) == '"lol"'

def test_empty_message():
    assert Extractors.message(**{}) is None

def test_success():
    assert Extractors.success(**{'success': True}) == 'SUCCESS'
    assert Extractors.success(**{'success': False}) == 'ERROR'
    assert Extractors.success(**{}) == 'UNKNOWN'

def test_auto():
    assert Extractors.auto(**{}) == 'MANUAL'
    assert Extractors.auto(**{'auto': True}) == 'AUTO'
    assert Extractors.auto(**{'auto': False}) == 'MANUAL'

def test_full_function():
    assert Extractors.function(**{'function': 'lol'}) == f'where: {BaseSettings.service_name}.lol()'
    assert Extractors.function(**{'function': 'lol', 'module': 'kek'}) == f'where: {BaseSettings.service_name}.kek.lol()'

def test_empty_function():
    assert Extractors.function(**{}) == f'where: {BaseSettings.service_name}.?'

def test_full_input_variables():
    vars = json_vars(1, 2, 3, lol='kek')
    assert Extractors.input_variables(**{'input_variables': vars}) == 'input variables: 1 (int), 2 (int), 3 (int), lol = "kek" (str)'

def test_empty_input_variables():
    assert Extractors.input_variables(**{}) is None

"""def test_full_local_variables():
    normal_vars = json_vars(lol='kek', kek='lol')
    not_normal_vars = json_vars(1, 2, 3, lol='kek', kek='lol')
    error_vars = 'lol'
    normal_vars = json_vars(locals())
    import json
    print(Extractors.local_variables(**{'local_variables': normal_vars}))
    assert Extractors.local_variables(**{'local_variables': normal_vars}) == 'local_variables: lol = "kek" (str), kek = "lol" (str)'
"""
def test_empty_local_variables():
    assert Extractors.local_variables(**{}) is None
