import json
import datetime
import pytest
from polog.handlers.file.base_formatter_fields_extractors import BaseFormatterFieldsExtractors as Extractors
from polog.core.utils.get_traceback import get_traceback
from polog import config, json_vars
from polog.core.settings_store import SettingsStore


def test_full_time():
    """
    Проверяем форматирование даты и времени лога.
    """
    tag = datetime.datetime(2021, 2, 7, 23, 46)
    tag_string = '[2021-02-07 23:46:00]'
    assert Extractors.time(**{'time': tag}) == tag_string

def test_empty_time():
    """
    Проверка, что при отсутствии поля time возвращается None.
    """
    assert Extractors.time(**{}) == '[----time not specified----]'

def test_full_level():
    """
    Проверяем, что level выводится по имени, если имя зарегистрировано, иначе - числом.
    """
    assert Extractors.level(**{'level': 123}) == '123'
    config.levels(SOMELEVEL=123)
    assert Extractors.level(**{'level': 123}) == 'SOMELEVEL'

def test_empty_level():
    """
    Проверка, что при отсутствии поля level возвращается None.
    """
    assert Extractors.level(**{}) == 'UNKNOWN'

def test_full_message():
    """
    Проверяем, что message выводится в двойных кавычках, без префиксов.
    Позиция message всегда фиксирована, на префиксах мы экономим символы.
    """
    assert Extractors.message(**{'message': 'lol'}) == '"lol"'

def test_empty_message():
    """
    Проверка, что при отсутствии поля message возвращается None.
    """
    assert Extractors.message(**{}) is None

def test_success():
    """
    Проверка, что конкретно форматируется метка успешности операции.
    """
    assert Extractors.success(**{'success': True}) == 'SUCCESS'
    assert Extractors.success(**{'success': False}) == 'ERROR'
    assert Extractors.success(**{}) == 'UNKNOWN'

def test_auto():
    """
    Проверка, что конкретно форматируется о том, автоматический лог или нет.
    """
    assert Extractors.auto(**{}) == 'MANUAL'
    assert Extractors.auto(**{'auto': True}) == 'AUTO'
    assert Extractors.auto(**{'auto': False}) == 'MANUAL'

def test_full_function():
    """
    Поля function и module визуально объединяются, также к ним конкатенируется имя сервиса.
    Проверяем, что это происходит. Проверяем наличие префикса "where: ".
    """
    assert Extractors.function(**{'function': 'lol'}) == f'where: {SettingsStore.service_name}.lol()'
    assert Extractors.function(**{'function': 'lol', 'module': 'kek'}) == f'where: {SettingsStore.service_name}.kek.lol()'

def test_empty_function():
    """
    Проверка, что при отсутствии поля function возвращается None.
    """
    assert Extractors.function(**{}) == f'where: {SettingsStore.service_name}.?'

def test_full_input_variables():
    """
    Проверка, что входные параметры функции форматируются корректно.

    Префикс должен быть "input variables: ". Затем должно идти перечисление переменных через запятую, при этом выводится содержимое переменной и ее тип в скобках. Строки выводятся в двойных кавычках.
    """
    vars = json_vars(1, 2, 3, lol='kek')
    assert Extractors.input_variables(**{'input_variables': vars}) == 'input variables: 1 (int), 2 (int), 3 (int), lol = "kek" (str)'

def test_empty_input_variables():
    """
    Проверка, что при отсутствии поля input_variables возвращается None.
    """
    assert Extractors.input_variables(**{}) is None
    assert Extractors.input_variables(**{'input_variables': ''}) is None

def test_full_local_variables():
    """
    Форматирование локальных переменных.

    Локальные переменные могут быть как записаны автоматически, так и переданы пользователем вручную.
    Автоматически запись происходит в формате json со стандартной для переменных схемой (см. функцию json_vars). Если формат записи совпадает с этой схемой, форматируем стандартно. Иначе - просто вставляем в лог пользовательскую запись в данном им виде.
    """
    normal_vars = json_vars(lol='kek', kek='lol')
    not_normal_vars = json_vars(1, 2, 3, lol='kek', kek='lol')
    error_vars = 'lol'
    assert Extractors.local_variables(**{'local_variables': normal_vars}) == 'local variables: lol = "kek" (str), kek = "lol" (str)'
    assert Extractors.local_variables(**{'local_variables': not_normal_vars}) == 'local variables: 1 (int), 2 (int), 3 (int), lol = "kek" (str), kek = "lol" (str)'
    assert Extractors.local_variables(**{'local_variables': error_vars}) == 'local variables: lol'

def test_empty_local_variables():
    """
    Проверка, что при отсутствии поля local_variables возвращается None.
    """
    assert Extractors.local_variables(**{}) is None
    assert Extractors.local_variables(**{'local_variables': ''}) is None

def test_time_of_work_full():
    """
    Форматирование времени работы функции.
    """
    assert Extractors.time_of_work(**{'time_of_work': 1.0}) == 'time of work: 1 sec.'
    assert Extractors.time_of_work(**{'time_of_work': 1.534}) == 'time of work: 1.534 sec.'
    assert Extractors.time_of_work(**{'time_of_work': 1.5}) == 'time of work: 1.5 sec.'
    # Проверяем ограничение в 8 знаков после запятой.
    assert Extractors.time_of_work(**{'time_of_work': 1.5345653557557657657}) == 'time of work: 1.53456536 sec.'

def test_time_of_work_empty():
    """
    Проверка, что при отсутствии поля time_of_work возвращается None.
    """
    assert Extractors.time_of_work(**{}) is None

def test_exception_full():
    """
    Поля exception_type и exception_message объединяются. Проверяем форматирование.
    """
    assert Extractors.exception(**{'exception_type': 'ValueError', 'exception_message': 'lol'}) == 'exception: ValueError("lol")'

def test_exception_empty():
    """
    Проверка, что корректно возвращается None при незаполненных полях об исключении.
    """
    assert Extractors.exception(**{}) is None

def test_traceback_empty():
    """
    Проверка, что при отсутствии поля traceback возвращается None.
    """
    assert Extractors.traceback(**{}) is None

def test_traceback_full():
    """
    Проверка базовых условий форматирования трейсбэка.
    """
    assert Extractors.traceback(**{'traceback': ''}) == 'no traceback'
    try:
        raise ValueError('lol')
    except:
        trace = get_traceback()
        handled_trace = Extractors.traceback(**{'traceback': trace})
        assert handled_trace.startswith('traceback: ')
        assert len(handled_trace) > len('traceback: ')
        assert "raise ValueError('lol')" in handled_trace
        assert "in test_traceback_full" in handled_trace
