import pytest

from polog.errors import LoggedError, IncorrectUseOfTheDecoratorError, DoubleSettingError, AfterStartSettingError, RewritingLogError


errors = [LoggedError, IncorrectUseOfTheDecoratorError, DoubleSettingError, AfterStartSettingError, RewritingLogError]

def test_multiraise():
    """
    Проверяем, что исключения поднимаются.
    """
    for error in errors:
        with pytest.raises(error):
            raise error
