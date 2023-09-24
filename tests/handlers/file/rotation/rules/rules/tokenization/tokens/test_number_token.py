import pytest

from polog.handlers.file.rotation.rules.rules.tokenization.tokens.number_token import NumberToken


def test_content_extraction_for_number_token():
    """
    Проверяем, что значение из строки извлекается корректно.
    """
    assert NumberToken('20').content == 20
    assert NumberToken('0').content == 0
    assert NumberToken('-0').content == 0
    assert NumberToken('-1000').content == -1000
    assert NumberToken('34340').content == 34340

def test_equal_to_number_token():
    """
    Проверяем, что проверка на равенство универсального токена работает корректно.
    """
    assert NumberToken('20') == NumberToken('20')
    assert NumberToken('0') == NumberToken('0')
    assert NumberToken('-0') == NumberToken('0')

    assert NumberToken('20') != NumberToken('21')
    assert NumberToken('20') != NumberToken('-20')

def test_str_representation_of_number_token():
    """
    Пробуем преобразовать токен в строку при помощи str(), должно срабатывать.
    """
    assert str(NumberToken('20')) == 'NumberToken(20)'

def test_creating_number_token_with_error():
    """
    Проверяем, что, если строка не является числом, токен не создастся.
    """
    with pytest.raises(ValueError):
        NumberToken('kek')
