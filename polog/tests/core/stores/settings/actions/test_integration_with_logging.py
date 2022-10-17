import logging
from datetime import datetime

from polog import config


def test_integration_with_logging_on_simple_error(handler):
    """
    Проверяем, что интеграция с logging с уровнем error работает.
    """
    config.set(pool_size=0, integration_with_logging=True)

    before = datetime.now()
    logging.error('kek')
    after = datetime.now()


    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['level'] == 40
    assert handler.last['message'] == 'kek'
    assert handler.last['level'] == 40

    assert isinstance(handler.last['time'], datetime)
    assert before < handler.last['time']
    assert handler.last['time'] < after

    assert handler.last['thread'].startswith('MainThread (')
    assert handler.last['thread'].endswith(')')
    assert handler.last['thread'][12:-1].isdigit()

    assert handler.last['process'].startswith('MainProcess (')
    assert handler.last['process'].endswith(')')
    assert handler.last['process'][13:-1].isdigit()

    assert handler.last['from_logging'] == True

    assert handler.last['function'] == 'test_integration_with_logging_on_simple_error'
    assert handler.last['line_number'] == 11
    assert handler.last['module'] == 'test_integration_with_logging'
    assert handler.last['path_to_code'].endswith('/actions/test_integration_with_logging.py')

    assert handler.last['auto'] == False
    assert handler.last['success'] == False

def test_integration_with_logging_on_off_on(handler):
    """
    Проверяем, что, если интеграцию с logging включить, выключить, а потом снова включить, сообщения, соответственно, будут, не будут, и опять будут попадать в Polog.
    """
    config.set(pool_size=0, integration_with_logging=True)

    logging.error('kek')
    assert handler.last is not None
    handler.clean()

    config.set(pool_size=0, integration_with_logging=False)
    logging.error('kek')
    assert handler.last is None
    handler.clean()

    config.set(pool_size=0, integration_with_logging=True)
    logging.error('kek')
    assert handler.last is not None
    handler.clean()

def test_integration_with_logging_on_simple_exception(handler):
    """
    Проверяем, что интеграция с logging работает, когда лог пишется через функцию exception().
    """
    config.set(pool_size=0, integration_with_logging=True)

    before = datetime.now()
    try:
        raise ValueError
    except:
        logging.exception('kek')
    after = datetime.now()


    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['level'] == 40
    assert handler.last['message'] == 'kek'
    assert handler.last['level'] == 40

    assert isinstance(handler.last['time'], datetime)
    assert before < handler.last['time']
    assert handler.last['time'] < after

    assert handler.last['thread'].startswith('MainThread (')
    assert handler.last['thread'].endswith(')')
    assert handler.last['thread'][12:-1].isdigit()

    assert handler.last['process'].startswith('MainProcess (')
    assert handler.last['process'].endswith(')')
    assert handler.last['process'][13:-1].isdigit()

    assert handler.last['from_logging'] == True

    assert handler.last['function'] == 'test_integration_with_logging_on_simple_error'
    assert handler.last['line_number'] == 11
    assert handler.last['module'] == 'test_integration_with_logging'
    assert handler.last['path_to_code'].endswith('/actions/test_integration_with_logging.py')

    assert handler.last['auto'] == False
    assert handler.last['success'] == False

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kek'
