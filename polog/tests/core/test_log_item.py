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
    log_id = id(log)

    # Пустой лог.
    assert str(log) == '<log item #' + str(log_id) + ' (empty)>'

    # Вывод с одним полем (строкой).
    log.set_data({'lol': 'kek'})
    assert str(log) == '<log item #' + str(log_id) + ' with content: lol = "kek">'

    # Проверка, что строковые репрезентации двух разных логов - разные (за счет id).
    log_2 = LogItem()
    log_2.set_data({'lol': 'kek'})
    assert str(log) != str(log_2)

    # Вывод с несколькими полями. Строковые поля должны выводиться в двойных кавычках, остальные - как есть.
    log_3 = LogItem()
    log_3.set_data({'cheburek': 'shmek', 'perekek': 5, 'perekekoperekek': True})
    log_3_id = id(log_3)
    assert str(log_3) == '<log item #' + str(log_3_id) + ' with content: cheburek = "shmek", perekek = 5, perekekoperekek = True>'

    # Проверяем, что, если контент лога задан в виде пустого словаря, он тоже отображается как пустой.
    log_4 = LogItem()
    log_4.set_data({})
    log_4_id = id(log_4)
    assert str(log_4) == '<log item #' + str(log_4_id) + ' (empty)>'

def test_get_field_content_from_log_with_brackets():
    """
    Извлекаем значение из лога с помощью квадратных скобок.
    """
    log = LogItem()

    # Словарь с контентом лога не задан, при этом все равно должно быть KeyError.
    with pytest.raises(KeyError):
        log['kek']

    # Словарь с контентом лога уже задан, но содержимого по данному ключу в нем нет, должно подниматься KeyError.
    log.set_data({})
    with pytest.raises(KeyError):
        log['kek']

    # Словарь с контентом лога задан, по ключу должно возвращаться значение.
    log = LogItem()
    log.set_data({'lol': 'kek'})
    assert log['lol'] == 'kek'
