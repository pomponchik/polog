import pytest

from polog.core.utils.name_manager import NameManager


def test_is_possible_level_name():
    """
    Проверяем, что определение корректности имен уровней логирования работает корректно.
    """
    assert NameManager.is_possible_level_name('lol kek').possibility == False
    assert NameManager.is_possible_level_name('_kek').possibility == False
    assert NameManager.is_possible_level_name('.kek').possibility == False
    assert NameManager.is_possible_level_name('message').possibility == False

    assert NameManager.is_possible_level_name('kek').possibility == True

def test_is_possible_extra_field_name():
    """
    Проверяем, что определение корректности имен извлекаемых полей работает корректно.
    """
    assert NameManager.is_possible_extra_field_name('lol kek').possibility == False
    assert NameManager.is_possible_extra_field_name('_kek').possibility == False
    assert NameManager.is_possible_extra_field_name('.kek').possibility == False

    assert NameManager.is_possible_extra_field_name('message').possibility == False
    assert NameManager.is_possible_extra_field_name('level').possibility == False
    assert NameManager.is_possible_extra_field_name('auto').possibility == False
    assert NameManager.is_possible_extra_field_name('time').possibility == False
    assert NameManager.is_possible_extra_field_name('service_name').possibility == False
    assert NameManager.is_possible_extra_field_name('success').possibility == False
    assert NameManager.is_possible_extra_field_name('function').possibility == False
    assert NameManager.is_possible_extra_field_name('class').possibility == False
    assert NameManager.is_possible_extra_field_name('exception_type').possibility == False
    assert NameManager.is_possible_extra_field_name('exception_message').possibility == False
    assert NameManager.is_possible_extra_field_name('traceback').possibility == False
    assert NameManager.is_possible_extra_field_name('input_variables').possibility == False
    assert NameManager.is_possible_extra_field_name('local_variables').possibility == False
    assert NameManager.is_possible_extra_field_name('result').possibility == False
    assert NameManager.is_possible_extra_field_name('time_of_work').possibility == False

    assert NameManager.is_possible_extra_field_name('kek').possibility == True

def test_is_identifier_name():
    """
    Проверяем, что определение строки как возможного идентификатора python работает корректно.
    """
    assert NameManager.is_identifier_name('PossibleName') == True
    assert NameManager.is_identifier_name('possible_name') == True
    assert NameManager.is_identifier_name('kek') == True
    assert NameManager.is_identifier_name('__kek') == True

    assert NameManager.is_identifier_name('.kek') == False
    assert NameManager.is_identifier_name('lol kek') == False
