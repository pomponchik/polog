import time

import pytest

from polog import config, flog, field, log
from polog.core.utils.exception_escaping import exception_escaping


def ip_extractor(log):
    request = log.function_input_data.args[0]
    ip = request.META.get('REMOTE_ADDR')
    return ip

class Request:
    META = {'REMOTE_ADDR': '123.456.789.010'}


def test_django_example(handler):
    """
    Проверяем, что пример кода из README.md работает.
    В данном случае мы проверяем, что извлекается ip-адрес из обработчика запросов Django.
    """
    config.add_fields(ip=field(ip_extractor))

    @flog
    def django_handler_example(request):
        html = 'text'
        return html
    request = Request()

    django_handler_example(request)

    time.sleep(0.0001)
    assert handler.last['ip'] == '123.456.789.010'

def test_django_example_error(handler):
    """
    В README.md есть пример кода с извлечением ip-адреса в обработчике запроса Django.
    В данном теста мы проверяем, что он работает.
    """
    config.add_fields(ip=field(ip_extractor))

    @flog
    def django_handler_error(request):
        html = 1 / 0
        return html
    request = Request()
    try:
        django_handler_error(request)
    except:
        pass
    time.sleep(0.0001)
    assert handler.last['ip'] == '123.456.789.010'

def test_not_called_extractor():
    """
    Скармливаем невызываемый объект в виде экстрактора.
    """
    with pytest.raises(ValueError):
        field('kek')

def test_not_called_converter():
    """
    Скармливаем невызываемый объект в виде конвертера.
    """
    with pytest.raises(ValueError):
        field(ip_extractor, converter='kek')

def test_basic_converter(handler):
    """
    Указываем конвертер значений и проверяем, что он работает.
    """
    @flog
    def django_handler_example(request):
        html = 'text'
        return html
    request = Request()
    config.add_fields(ip_converted=field(ip_extractor, converter=lambda value: 'converted_' + value))

    django_handler_example(request)

    time.sleep(0.0001)
    assert handler.last['ip_converted'] == 'converted_123.456.789.010'

def test_not_correct_extractor_signature():
    """
    Пробуем передать в качестве экстрактора функцию, чья сигнатура не соответствует ожидаемой.
    """
    def not_extractor(a, b, c):
        pass

    with pytest.raises(ValueError):
        config.add_fields(data=field(not_extractor))

def test_not_correct_converter_signature():
    """
    Пробуем передать в качестве конвертера функцию, чья сигнатура не соответствует ожидаемой.
    """
    def extractor(log_item):
        pass

    def not_converter(a, b, c):
        pass

    with pytest.raises(ValueError):
        config.add_fields(data=field(extractor, converter=not_converter))

def test_field_through_data_passage_with_decorator(handler):
    """
    Проверяем, что данные из экстрактора проходят насквозь без какой-либо конвертации (например без преобразования в строку).
    """
    config.set(pool_size=0)
    def extractor(log_item):
        return 1
    config.add_fields(data=field(extractor))

    @log(message='kek')
    def kek():
        pass

    kek()

    assert handler.last['data'] == 1

def test_field_through_data_passage_with_error_decorator(handler):
    """
    Аналог теста test_field_through_data_passage(), но теперь внутри обернутой функции происходит исключение.
    """
    config.set(pool_size=0)
    def extractor(log_item):
        return 1
    config.add_fields(data=field(extractor))

    @exception_escaping
    @log(message='kek')
    def kek():
        raise ValueError

    kek()

    assert handler.last['data'] == 1

def test_field_through_data_passage_with_handle_logging(handler):
    """
    Аналог теста test_field_through_data_passage(), но вместо декоратора проверяем ручное логирование.
    """
    config.set(pool_size=0)
    def extractor(log_item):
        return 1
    config.add_fields(data=field(extractor))

    log('kek')

    assert handler.last['data'] == 1
