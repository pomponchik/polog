import pytest
from polog.errors import RewritingLogError
from polog.core.log_item import LogItem


def test_init_empty_log():
    """
    Проверяем, что инстанс лога без аргументов создается.
    """
    log = LogItem()

def test_set_field_to_log_error():
    """
    Проверяем, что при попытке изменить содержимое поля лога через синтаксис словаря поднимается специальное исключение (RewritingLogError).
    """
    log = LogItem()
    with pytest.raises(RewritingLogError):
        log['kek'] = 'lol'

def test_delete_field_from_log_error():
    """
    Проверяем, что при попытке удалить содержимое поля лога через синтаксис словаря поднимается специальное исключение (RewritingLogError).
    """
    log = LogItem()

    # Когда такого ключа нет.
    with pytest.raises(RewritingLogError):
        del log['kek']

    log.set_data({'lol': 'kek'})
    # Когда ключ есть.
    with pytest.raises(RewritingLogError):
        del log['lol']

def test_log_to_string_representstion():
    """
    Проверяем, что преобразование лога в строку работает корректно как в случае пустого лога, так и в случае заполненного.
    """
    log = LogItem()

    assert str(log) == '<log item #' + str(log_id) + ' (empty)>'

    log.set_data({'lol': 'kek'})
    log_id = id(log)
    assert str(log) == '<log item #' + str(log_id) + ' with content: lol = "kek">'

    log_2 = LogItem()
    log_2.set_data({'lol': 'kek'})
    assert str(log) != str(log_2)

    log_3 = LogItem()
    log_2.set_data({'cheburek': 'shmek', 'perekek': 5, 'perekekoperekek': True})
    log_3_id
    assert str(log) == '<log item #' + str(log_3_id) + ' with content: cheburek = "shmek", perekek = 5, perekekoperekek = True>'
