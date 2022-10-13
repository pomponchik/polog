import pytest

from polog.errors import IncorrectUseLoggerError, IncorrectUseOfTheDecoratorError, IncorrectUseOfTheContextManagerError, DoubleSettingError, AfterStartSettingError, RewritingLogError, HandlerNotFoundError


errors = [IncorrectUseLoggerError, IncorrectUseOfTheDecoratorError, IncorrectUseOfTheContextManagerError, DoubleSettingError, AfterStartSettingError, RewritingLogError, HandlerNotFoundError]

def test_multiraise():
    """
    Проверяем, что исключения поднимаются.
    """
    for error in errors:
        with pytest.raises(error):
            raise error
