import time
import datetime

import pytest

from polog.errors import RewritingLogError
from polog.core.log_item import LogItem, FunctionInputData


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


def test_get_field_content_from_log_with_method_get():
    """
    Извлекаем значение из лога с помощью метода .get().
    Со значениями по умолчанию и без.
    """
    log = LogItem()

    # Словарь с контентом лога не задан, возвращаться должно значение по умолчанию.
    assert log.get('kek') is None
    assert log.get('kek', 'lol') == 'lol'

    # Словарь с контентом лога уже задан, но содержимого по данному ключу в нем нет, должно возвращаться значение по умолчанию.
    log.set_data({})
    assert log.get('kek') is None
    assert log.get('kek', 'lol') == 'lol'

    # Словарь с контентом лога задан, по ключу должно возвращаться значение.
    log = LogItem()
    log.set_data({'lol': 'kek'})
    assert log.get('lol') == 'kek'
    assert log.get('lol', 'no_kek') == 'kek'


def test_operator_in():
    """
    Проверяем, что оператор in по отношению к логу работает корректно.
    """
    # Совсем пустой лог.
    log = LogItem()
    assert ('lol' in log) == False

    # Лог, где нет указанного ключа.
    log_2 = LogItem()
    log_2.set_data({})
    assert ('lol' in log_2) == False

    # Лог, где есть указанный ключ.
    log_3 = LogItem()
    log_3.set_data({'lol': 'kek'})
    assert ('lol' in log_3) == True


def test_iteration_by_log():
    """
    Проверяем, что по объекту лога можно итерироваться как по словарю.
    """
    log = LogItem()

    # Совсем пустой лог.
    count = 0
    for key in log:
        count += 1
    assert count == 0

    # Лог, где нет ни одного поля.
    log.set_data({})
    count = 0
    for key in log:
        count += 1
    assert count == 0

    # Лог с 1 полем.
    log = LogItem()
    log.set_data({'lol': 'kek'})
    count = 0
    for key in log:
        count += 1
    assert count == 1

    # Лог с 3 полями. Проверяем как количество итераций, так и корректность возвращаемых ключей при итерации.
    log = LogItem()
    data = {'lol': 'kek', 'cheburek': 'perekek', 'pek': 'shmek'}
    log.set_data(data)
    count = 0
    keys = []
    for key in log:
        count += 1
        keys.append(key)
        assert log[key] == data[key]
    assert count == 3
    assert keys == list(data.keys())


def test_equal_logs():
    """
    Проверяем, что проверка логов на равенство работает.
    """
    false_log_1 = LogItem()
    false_log_1.set_data({'lol': 'kek'})
    false_log_2 = LogItem()
    false_log_2.set_data({'time': datetime.datetime.now()})
    false_log_3 = LogItem()
    false_log_3.set_data({'lol': 'kek'})
    false_log_4 = LogItem()
    false_log_4.set_data({'lol': 'kek'})

    # Очевидное.
    assert LogItem() != 5
    assert LogItem() != 'kek'
    assert LogItem() != false_log_1
    assert LogItem() != false_log_2

    # Не очевидный момент. Сравнение производится по полю 'time', поэтому даже 2 полностью идентичных лога без данного поля не считаются равными.
    assert false_log_3 != false_log_4

    # Два лога с разными метками времени, не считаются равными.
    log_1 = LogItem()
    log_1.set_data({'time': datetime.datetime.now()})
    time.sleep(0.00001)
    log_2 = LogItem()
    log_2.set_data({'time': datetime.datetime.now()})
    assert log_1 != log_2

    # Ситуация условного равенства двух логов, когда у них обоих одна и та же метка 'time'.
    data = {'time': datetime.datetime.now()}
    log_1 = LogItem()
    log_2 = LogItem()
    log_1.set_data(data)
    log_2.set_data(data)
    assert log_1 is not log_2
    assert log_1 == log_2


def test_other_comparisons():
    """
    Проверяем работу прочих операторов сравнения.
    """
    log_1 = LogItem()
    log_1.set_data({'time': datetime.datetime.now()})

    time.sleep(0.00001)

    log_2 = LogItem()
    log_2.set_data({'time': datetime.datetime.now()})

    empty_log_1 = LogItem()
    empty_log_2 = LogItem()

    assert log_2 > log_1
    with pytest.raises(TypeError) as exception_info:
        log_1 > 5
    assert str(exception_info.value) == "'>' not supported between instances of 'LogItem' and 'int'"
    with pytest.raises(TypeError):
        empty_log_1 > empty_log_2

    assert log_2 >= log_1
    with pytest.raises(TypeError) as exception_info:
        log_1 >= 5
    assert str(exception_info.value) == "'>=' not supported between instances of 'LogItem' and 'int'"
    with pytest.raises(TypeError):
        empty_log_1 >= empty_log_2

    assert log_1 < log_2
    with pytest.raises(TypeError) as exception_info:
        log_1 < 5
    assert str(exception_info.value) == "'<' not supported between instances of 'LogItem' and 'int'"
    with pytest.raises(TypeError):
        empty_log_1 < empty_log_2

    assert log_1 <= log_2
    with pytest.raises(TypeError) as exception_info:
        log_1 <= 5
    assert str(exception_info.value) == "'<=' not supported between instances of 'LogItem' and 'int'"
    with pytest.raises(TypeError):
        empty_log_1 <= empty_log_2


def test_get_items():
    """
    Проверяем работу метода .items(). Должно работать по аналогии со словарем.
    """
    log = LogItem()

    assert log.items() == ()

    log.set_data({'lol': 'kek'})

    assert tuple(log.items()) == (('lol', 'kek'), )


def test_get_keys():
    """
    Проверяем работу метода .keys(). Должно работать по аналогии со словарем.
    """
    log = LogItem()

    assert log.keys() == ()

    log.set_data({'lol': 'kek'})

    assert tuple(log.keys()) == ('lol', )


def test_get_values():
    """
    Проверяем работу метода .keys(). Должно работать по аналогии со словарем.
    """
    log = LogItem()

    assert log.values() == ()

    log.set_data({'lol': 'kek'})

    assert tuple(log.values()) == ('kek', )


def test_function_input_data_set_and_get():
    """
    Проверяем, что атрибут .function_input_data заполняется корректно.
    """
    log = LogItem()

    assert isinstance(log.function_input_data, FunctionInputData)
    assert log.function_input_data.args is None
    assert log.function_input_data.kwargs is None

    args = ('lol', 'kek')
    kwargs = {'lol': 'kek', 'cheburek': 'perekekoperekek'}
    log.set_function_input_data(args, kwargs)

    assert log.function_input_data.args == args
    assert log.function_input_data.kwargs == kwargs

def test_handlers_set_and_get():
    """
    Обработчики хранятся прямо в объекте лога.
    Проверяем, что они в нем сохраняются, и из него извлекаются.
    """
    log = LogItem()

    assert log.get_handlers() == ()

    # Имитируем коллекцию обработчиков данным списком.
    lst = [1, 2, 3, 4, 5]
    log.set_handlers(lst)

    assert log.get_handlers() == lst
