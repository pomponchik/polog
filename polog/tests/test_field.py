import time
import pytest
from polog import config, flog, field


def ip_extractor(function_input, **kwargs):
    request = function_input[0][0]
    ip = request.META.get('REMOTE_ADDR')
    return ip

config.add_fields(ip=field(ip_extractor))


class Request:
    META = {'REMOTE_ADDR': '123.456.789.010'}

def test_django_example(handler):
    """
    Проверяем, что пример кода из README.md работает.
    В данном случае мы проверяем, что извлекается ip-адрес из обработчика запросов Django.
    """
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
