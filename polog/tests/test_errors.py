import pytest
from polog.errors import LoggedError, IncorrectUseOfTheDecoratorError, DoubleSettingError, AfterStartSettingError


errors = [LoggedError, IncorrectUseOfTheDecoratorError, DoubleSettingError, AfterStartSettingError]

def test_multiraise():
    """
    Проверяем, что исключения поднимаются.
    """
    for error in errors:
        with pytest.raises(error):
            raise error
