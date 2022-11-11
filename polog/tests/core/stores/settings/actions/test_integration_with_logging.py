import logging
from datetime import datetime
import time

from polog import config


def test_integration_with_logging_on_simple_error(handler):
    """
    Проверяем, что интеграция с logging с уровнем error работает.
    """
    config.set(pool_size=0, logging_off=False, integration_with_logging=True)

    before = datetime.fromtimestamp(time.perf_counter())
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
    assert handler.last['line_number'] == 14
    assert handler.last['module'] == 'test_integration_with_logging'
    assert handler.last['path_to_code'].endswith('/actions/test_integration_with_logging.py')

    assert handler.last['auto'] == False
    assert handler.last['success'] == False

def test_integration_with_logging_on_off_on(handler):
    """
    Проверяем, что, если интеграцию с logging включить, выключить, а потом снова включить, сообщения, соответственно, будут, не будут, и опять будут попадать в Polog.
    """
    config.set(pool_size=0, logging_off=False, integration_with_logging=True)

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
    config.set(pool_size=0, logging_off=False, integration_with_logging=True)

    before = datetime.now()
    try:
        raise ValueError('kekokek')
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

    assert handler.last['function'] == 'test_integration_with_logging_on_simple_exception'
    assert handler.last['line_number'] == 76
    assert handler.last['module'] == 'test_integration_with_logging'
    assert handler.last['path_to_code'].endswith('/actions/test_integration_with_logging.py')

    assert handler.last['auto'] == False
    assert handler.last['success'] == False

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kekokek'

def test_integration_on_logging_off_on_and_off(handler):
    """
    Проверяем, что настройка 'logging_off', выставленная в режим True, действительно останавливает работу logging, не затрагивая при этом Polog.
    """
    # Взято отсюда: https://stackoverflow.com/a/36408692/14522393
    class ListHandler(logging.Handler):
        def __init__(self, log_list):
            logging.Handler.__init__(self)
            self.lst = log_list
        def emit(self, record):
            self.lst.append(record)

    lst = []
    logging_handler = ListHandler(lst)
    logging.root.addHandler(logging_handler)

    config.set(integration_with_logging=True, logging_off=True)

    logging.error('kek')

    assert len(lst) == 0
    assert len(handler.all) == 1

    config.set(integration_with_logging=True, logging_off=False)

    logging.error('kek')

    assert len(lst) == 1
    assert len(handler.all) == 2

    logging.root.removeHandler(logging_handler)
