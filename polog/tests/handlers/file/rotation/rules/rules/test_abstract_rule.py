import pytest

from polog.handlers.file.rotation.rules.rules.abstract_rule import AbstractRule


def test_abstract_rule_repr_method():
    """
    Проверяем, что у экземпляров отнаследованного класса корректно работает строковая репрезентация содержимого.
    """
    class KekRule(AbstractRule):
        def prove_source(self):
            return False

    assert str(KekRule('kek', None)) == 'KekRule("kek")'
