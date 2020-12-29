from polog.base_settings import BaseSettings
from polog.errors import LoggedError


def reraise_exception(exc):
    """
    Функция, где решается, какое исключение поднять - оригинальное или встроенное в Polog, в зависимости от настроек.
    """
    if BaseSettings().original_exceptions:
        raise exc
    raise LoggedError(str(exc)) from exc
