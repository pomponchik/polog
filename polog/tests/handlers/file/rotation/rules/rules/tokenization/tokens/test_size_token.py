import pytest

from polog.handlers.file.rotation.rules.rules.tokenization.tokens.size_token import SizeToken


def test_content_extraction_for_size_token():
    """
    Проверяем, что значение из строки извлекается корректно.
    """
    assert SizeToken('b').content == 1
    assert SizeToken('kb').content == 1024
    assert SizeToken('mb').content == 1024 * 1024
    assert SizeToken('gb').content == 1024 * 1024 * 1024
    assert SizeToken('tb').content == 1024 * 1024 * 1024 * 1024
    assert SizeToken('pb').content == 1024 * 1024 * 1024 * 1024 * 1024

    assert SizeToken('byte').content == 1
    assert SizeToken('kilobyte').content == 1024
    assert SizeToken('megabyte').content == 1024 * 1024
    assert SizeToken('gigabyte').content == 1024 * 1024 * 1024
    assert SizeToken('terabyte').content == 1024 * 1024 * 1024 * 1024
    assert SizeToken('petabyte').content == 1024 * 1024 * 1024 * 1024 * 1024

    assert SizeToken('bytes').content == 1
    assert SizeToken('kilobytes').content == 1024
    assert SizeToken('megabytes').content == 1024 * 1024
    assert SizeToken('gigabytes').content == 1024 * 1024 * 1024
    assert SizeToken('terabytes').content == 1024 * 1024 * 1024 * 1024
    assert SizeToken('petabytes').content == 1024 * 1024 * 1024 * 1024 * 1024
