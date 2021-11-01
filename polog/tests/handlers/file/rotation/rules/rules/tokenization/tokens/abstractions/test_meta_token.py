import pytest

from polog.handlers.file.rotation.rules.rules.tokenization.tokens.abstractions.meta_token import MetaToken


def test_raise_errors_in_metatoken():
    """
    Пробуем создавать "неправильные" классы на основе метакласса. Должны подниматься исключения.
    """
    with pytest.raises(AttributeError):
        class TestToken(metaclass=MetaToken):
            regexp_letter = '['

    with pytest.raises(AttributeError):
        class TestToken(metaclass=MetaToken):
            regexp_letter = ']'

    with pytest.raises(AttributeError):
        class TestToken(metaclass=MetaToken):
            regexp_letter = '*'

    with pytest.raises(AttributeError):
        class TestToken(metaclass=MetaToken):
            regexp_letter = 'lol'

    with pytest.raises(AttributeError):
        class TestToken(metaclass=MetaToken):
            pass

    with pytest.raises(AttributeError):
        class TestToken(metaclass=MetaToken):
            regexp_letter = True

    for letter in 'nsd':
        with pytest.raises(AttributeError):
            class TestToken(metaclass=MetaToken):
                regexp_letter = letter

    with pytest.raises(AttributeError):
        class AbstractToken(metaclass=MetaToken):
            regexp_letter = 'k'
