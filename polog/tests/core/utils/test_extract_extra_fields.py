import pytest
from polog import field
from polog.core.utils.extract_extra_fields import extract_extra_fields


def extractor_1(args, **kwargs):
    return 'hello'

def extractor_2(args, **kwargs):
    return 'world'

def extractor_3(args, **kwargs):
    return 3

def extractor_4(args, **kwargs):
    return 4

def extractor_5(args, **kwargs):
    return 5

def extractor_6(args, **kwargs):
    return 6

class FalseBaseSettings:
    extra_fields = {'hello': field(extractor_1), 'world': field(extractor_2)}

class FalseBaseSettings2:
    extra_fields = {'3': field(extractor_3, converter=lambda x: str(x) + ' converted'), '4': field(extractor_4, converter=lambda x: str(x) + ' converted')}

class FalseBaseSettings3:
    extra_fields = {'5': field(extractor_5), '6': field(extractor_6)}


def test_base():
    """
    Проверяем, что в базовом случае дополнительные поля извлекаются.
    """
    args_dict = {}
    extract_extra_fields(None, args_dict, settings=FalseBaseSettings())
    assert args_dict == {'hello': 'hello', 'world': 'world'}

def test_other_type_with_converter():
    """
    Проверяем, что все работает, если экстрактор поля возвращает не строковый объект, но используется конвертер.
    """
    args_dict = {}
    extract_extra_fields(None, args_dict, settings=FalseBaseSettings2())
    assert args_dict == {'3': '3 converted', '4': '4 converted'}

def test_other_type_without_converter():
    """
    Проверяем, что все работает, если экстрактор поля возвращает не строковый объект, и конвертер не используется.
    """
    args_dict = {}
    extract_extra_fields(None, args_dict, settings=FalseBaseSettings3())
    assert args_dict == {'5': '5', '6': '6'}
