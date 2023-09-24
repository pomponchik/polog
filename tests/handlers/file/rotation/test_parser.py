import pytest

from polog.handlers.file.rotation.parser import Parser
from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper


class RulesElectorMock:
    def __init__(self, file):
        pass
    def choose(self, source):
        return source

def test_parse_single_rule_with_mock(filename_for_test):
    """
    Проверяем, что содержимое строки передавалось в RulesElectorMock.
    """
    file = FileDependencyWrapper([filename_for_test], lock_type='thread+file')
    parser = Parser(file, elector=RulesElectorMock)

    assert parser.extract_rules('20 mb ') == ['20 mb']
    assert parser.extract_rules(',20 mb ,') == ['20 mb']

def test_parse_multiple_rules_with_mock(filename_for_test):
    """
    Проверяем, что строка корректно сплитится.
    """
    file = FileDependencyWrapper([filename_for_test], lock_type='thread+file')
    parser = Parser(file, elector=RulesElectorMock)

    assert parser.extract_rules('20 mb, 30 mb ') == ['20 mb', '30 mb']
    assert parser.extract_rules('20 mb; 30 mb ') == ['20 mb', '30 mb']

    assert parser.extract_rules('  20 mb   ; 30 mb    ') == ['20 mb', '30 mb']
    assert parser.extract_rules('  20 mb   , 30 mb    ') == ['20 mb', '30 mb']

    assert parser.extract_rules('  20 mb   , 30 mb  ,    ') == ['20 mb', '30 mb']
    assert parser.extract_rules(',,,, 20 mb   , 30 mb  ,    ') == ['20 mb', '30 mb']
