import re
import json
import datetime
from inspect import Signature
import pytest
from polog import json_vars, config
from polog.handlers.file.base_formatter import BaseFormatter


def test_first_step_of_initialization():
    """
    Проверяем, что первичная инициализация объекта прошла успешно.
    А именно, что у объекта есть атрибут сепаратора, который мы передали аргументом.
    """
    formatter = BaseFormatter('kek')
    assert formatter.separator == 'kek'

def test_second_step_of_initialization():
    """
    Инициализация форматтера производится в два этапа.
    На первом (см. test_first_step_of_initialization()) сохраняются переданные пользователем параметры. Первый этап происходит при создании объекта.
    Второй этап - получение и сохранение различных динамических параметров. Это происходит непосредственно перед первой записью лога. Так сделано, поскольку при инициализации объекта могут быть еще неизвестны некоторые из динамических параметров форматтера. К примеру, ширина поля для записи уровней логирования зависит от длины самого длинного названия уровня логирования. Уровни логирования добавляются динамически в процессе выполнения программы и мы до самой первой записи лога не знаем, какие они будут (при этом существует договоренность, что все настройки логирования клиент обязан производить до первой записи лога, то есть мы можем быть уверены, что динамически это переписывать в дальнейшем не придется).

    Здесь мы проверяем, что:
    1. У объекта форматтера появляются новые атрибуты после первого вызова;
    2. Они не переопределяются при последующих вызовах;
    3. Они определены только на уровне экземпляра (т. к. у нас может быть несколько экземпляров обработчиков, которые используют по-разному настроенные форматтеры).
    """
    formatter = BaseFormatter('\n')
    assert not hasattr(formatter, 'FIELD_HANDLERS')
    assert not hasattr(formatter, 'ALIGN_NORMS')
    formatter.get_formatted_string((1, 2), **{'lol': 'lol', 'kek': 'kek'})
    assert hasattr(formatter, 'FIELD_HANDLERS')
    assert hasattr(formatter, 'ALIGN_NORMS')
    # Проверка, что второй шаг инициализации делается ровно один раз.
    # То есть что созданные атрибуты не переопределяются на каждом вызове метода .get_formatted_string().
    first_id = id(formatter.FIELD_HANDLERS)
    formatter.get_formatted_string((1, 2), **{'lol': 'lol', 'kek': 'kek'})
    assert first_id == id(formatter.FIELD_HANDLERS)
    # Проверяем, что новые атрибуты создались у экземпляра, а не у класса.
    # Для этого создаем новый экземпляр и проверяем, что их там снова нет.
    formatter = BaseFormatter('\n')
    assert not hasattr(formatter, 'FIELD_HANDLERS')
    assert not hasattr(formatter, 'ALIGN_NORMS')

def test_get_base_field_handlers_parameters():
    """
    Проверяем, что обработчики для заданного набора полей существуют, их можно вызвать, и их сигнатура соответствует ожидаемому формату.
    """
    formatter = BaseFormatter('\n')
    handlers = formatter.get_base_field_handlers()
    field_names = (
        'time',
        'level',
        'success',
        'auto',
        'message',
        'function',
        'time_of_work',
        'input_variables',
        'local_variables',
        'result',
        'exception',
        'traceback',
    )
    for name in field_names:
        assert name in handlers
        handler = handlers[name]
        assert callable(handler)
        signature = Signature.from_callable(handler)
        parameters = list(signature.parameters.values())
        assert len(parameters) == 1
        assert parameters[0].kind == parameters[0].VAR_KEYWORD

def test_get_base_field_handlers_calls():
    """
    Пробуем скормить тестовые данные в базовые обработчики полей и смотрим на результат.

    В базовом случае должна возвращаться строка.
    Если мы скормили обработчику None, в некоторых случаях он может вернуть None, а в некоторых - строку.
    При любом раскладе не должно возникать исключений (иначе поле записано не будет и данные из лога потеряются).
    """
    formatter = BaseFormatter('\n')
    handlers = formatter.get_base_field_handlers()
    field_names_and_proves = {
        'time': (datetime.datetime.now(),),
        'level': (-5, 0, 1, 100, 'kek'),
        'success': (True, False, None),
        'auto': (True, False, None),
        'message': ('lol', 'kek', None),
        'function': ('lol', None),
        'time_of_work': (0.1, 2, None),
        'input_variables': (json_vars(1, 2, 3, kek='lol'), json_vars(), json_vars('lol'), json_vars(1, 2, 3), json_vars(kek='lol'), None),
        'local_variables': (json_vars(1, 2, 3, kek='lol'), json_vars(), json_vars('lol'), json_vars(1, 2, 3), json_vars(kek='lol'), 'kek', None),
        'result': (json_vars(1, 2, 3, kek='lol'), json_vars(), json_vars('lol'), json_vars(1, 2, 3), json_vars(kek='lol'), 'kek', None),
        'exception': {'exception_type': 'ValueError', 'exception_message': 'kek'},
        'traceback': (json.dumps([]), None),
    }
    for name in field_names_and_proves:
        handler = handlers[name]
        data_items = field_names_and_proves[name]
        if isinstance(data_items, tuple):
            for item in data_items:
                test_data = {name: item}
                if item is None:
                    assert handler(**test_data) is None or isinstance(handler(**test_data), str)
                else:
                    assert isinstance(handler(**test_data), str)
        elif isinstance(data_items, dict):
            assert isinstance(handler(**data_items), str)

def test_format():
    """
    Проверяем, что итоговая строка правильно склеивается из исходного словаря.
    """
    formatter = BaseFormatter('\n')
    assert formatter.format({'lol': 'lol', 'kek': 'kek'}) == 'lol | kek\n'
    formatter = BaseFormatter('cheburek')
    assert formatter.format({'lol': 'lol', 'kek': 'kek'}) == 'lol | kekcheburek'

def test_width_and_align():
    """
    Проверяем, что поля, по которым заданы нормы форматирования, таки форматируются по длине строки.
    Также проверяем, что поля, для которых специальных норм нет, не затрагиваются.
    """
    formatter = BaseFormatter('\n')
    formatter.get_formatted_string((1, 2), **{'lol': 'lol', 'kek': 'kek'})
    norms = formatter.ALIGN_NORMS
    data = {
        'level': '_',
        'success': '_',
        'auto': '_',
        'lol': 'kek',
    }
    formatter.width_and_align(data)
    assert len(data['lol']) == 3
    for key, value in data.items():
        if key in norms:
            norm_lenth = norms[key][0]
            assert len(value) >= norm_lenth
