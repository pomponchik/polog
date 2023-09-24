import pytest

from polog.handlers.file.rotation.rules.rules.tokenization.tokenizator import Tokenizator
from polog.handlers.file.rotation.rules.rules.tokenization.tokens import SizeToken, NumberToken, DotToken


def test_base_tokenization():
    """
    Проверяем, что исходная строка корректно бьется на токены.
    """
    assert Tokenizator('20').tokens.tokens == [NumberToken('20')]
    assert Tokenizator('0').tokens.tokens == [NumberToken('0')]
    assert Tokenizator('   0').tokens.tokens == [NumberToken('0')]
    assert Tokenizator('030').tokens.tokens == [NumberToken('30')]
    assert Tokenizator('-30').tokens.tokens == [NumberToken('-30')]

    assert Tokenizator('megabytes').tokens.tokens == [SizeToken('mb')]
    assert Tokenizator('mb').tokens.tokens == [SizeToken('mb')]
    assert Tokenizator('megabyte').tokens.tokens == [SizeToken('mb')]
    assert Tokenizator('gigabytes').tokens.tokens == [SizeToken('gb')]
    assert Tokenizator('gb').tokens.tokens == [SizeToken('gb')]
    assert Tokenizator('gigabyte').tokens.tokens == [SizeToken('gb')]
    assert Tokenizator('kilobytes').tokens.tokens == [SizeToken('kb')]
    assert Tokenizator('kb').tokens.tokens == [SizeToken('kb')]
    assert Tokenizator('kilobyte').tokens.tokens == [SizeToken('kb')]
    assert Tokenizator('bytes').tokens.tokens == [SizeToken('b')]
    assert Tokenizator('b').tokens.tokens == [SizeToken('b')]
    assert Tokenizator('byte').tokens.tokens == [SizeToken('b')]
    assert Tokenizator('petabytes').tokens.tokens == [SizeToken('pb')]
    assert Tokenizator('pb').tokens.tokens == [SizeToken('pb')]
    assert Tokenizator('petabyte').tokens.tokens == [SizeToken('pb')]
    assert Tokenizator('terabytes').tokens.tokens == [SizeToken('tb')]
    assert Tokenizator('tb').tokens.tokens == [SizeToken('tb')]
    assert Tokenizator('terabyte').tokens.tokens == [SizeToken('tb')]

    assert Tokenizator('kek').tokens.tokens == [DotToken('kek')]
    assert Tokenizator('lol').tokens.tokens == [DotToken('lol')]
    assert Tokenizator('12lol').tokens.tokens == [DotToken('12lol')]

    assert Tokenizator('lol kek cheburek 12 mb oh').tokens.tokens == [DotToken('lol'), DotToken('kek'), DotToken('cheburek'), NumberToken('12'), SizeToken('mb'), DotToken('oh')]
    assert Tokenizator('20 20').tokens.tokens == [NumberToken('20'), NumberToken('20')]
