import time
import pytest
from polog import config, flog, field


def ip_extractor(args, **kwargs):
    request = args[0][0]
    ip = request.META.get('REMOTE_ADDR')
    return ip

config.add_fields(ip=field(ip_extractor))
lst = []
add_item = lambda *args, **kwargs: lst.append({x: y for x, y in kwargs.items()})
config.add_handlers(add_item)

@flog
def django_handler_example(request):
    html = 'text'
    return html

@flog
def django_handler_error(request):
    html = 1 / 0
    return html

class Request:
    META = {'REMOTE_ADDR': '123.456.789.010'}

def test_django_example():
    """
    Проверяем, что пример кода из README.md работает.
    В данном случае мы проверяем, что извлекается ip-адрес из обработчика запросов Django.
    """
    request = Request()
    django_handler_example(request)
    time.sleep(0.0001)
    assert lst[0]['ip'] == '123.456.789.010'
    lst.pop()

def test_django_example_error():
    request = Request()
    try:
        django_handler_error(request)
    except:
        pass
    time.sleep(0.0001)
    assert lst[0]['ip'] == '123.456.789.010'
    lst.pop()
