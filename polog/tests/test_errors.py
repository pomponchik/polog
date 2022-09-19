import pytest

from polog.errors import IncorrectUseOfTheDecoratorError, DoubleSettingError, AfterStartSettingError, RewritingLogError, HandlerNotFoundError


errors = [IncorrectUseOfTheDecoratorError, DoubleSettingError, AfterStartSettingError, RewritingLogError, HandlerNotFoundError]

def test_multiraise():
    """
    Проверяем, что исключения поднимаются.
    """
    for error in errors:
        with pytest.raises(error):
            raise error
