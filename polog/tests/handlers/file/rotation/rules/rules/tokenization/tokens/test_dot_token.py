import pytest

from polog.handlers.file.rotation.rules.rules.tokenization.tokens.dot_token import DotToken
from polog.handlers.file.rotation.rules.rules.tokenization.tokens.number_token import NumberToken

def test_equal_to_dot_token():
    """
    Проверяем, что проверка на равенство универсального токена работает корректно.
    """
    assert DotToken('kek') == DotToken('kek')
    assert DotToken('lol') != DotToken('kek')
    assert DotToken('lol') != NumberToken('20')
    assert DotToken('lol') != True
