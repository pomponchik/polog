from polog.base_settings import BaseSettings
from polog.errors import LoggedError


def raise_exception(exc):
    if BaseSettings().original_exceptions:
        raise exc
    raise LoggedError(str(exc))
