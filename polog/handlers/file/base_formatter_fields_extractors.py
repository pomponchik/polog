import inspect
import importlib
import ujson as json
from polog.core.levels import Levels
from polog.core.settings_store import SettingsStore


class BaseFormatterFieldsExtractors:
    """
    Данный класс - хранилище функций, преобразующих исходные данные логов в строки нужного формата.

    Если метод возвращает None, поле не выводится в итоговую запись лога.
    """

    # Словарь, где ключи - кортежи из названий модулей и функций.
    # См. метод search_function_name().
    FULL_FUNCTIONS_NAMES = {}

    @staticmethod
    def time(**kwargs):
        """
        Выводим дату и время в квадратных скобках.
        """
        time = kwargs.get("time")
        if time is None:
            return '[----time not specified----]'
        return f'[{time}]'

    @staticmethod
    def level(**kwargs):
        """
        Выводим уровень лога. Если присвоено название - выводим его, иначе число.

        Важно: если одному уровню логирования присвоено несколько имен, выводится последнее из них.
        """
        level = kwargs.get('level')
        if level is None:
            return 'UNKNOWN'
        result = Levels.get_level_name(level)
        return result

    @staticmethod
    def message(**kwargs):
        """
        Выводим пользовательский комментарий к логу в двойных кавычках.
        """
        result = kwargs.get('message')
        if result is None:
            return None
        result = f'"{result}"'
        return result

    @staticmethod
    def success(**kwargs):
        """
        Выводим метку успешности операции.

        Существуют 3 опции успешности: 'SUCCESS', 'ERROR' и 'UNKNOWN'.
        Последний вариант присваивается в том случае, если информации об успешности операции нет.
        Как правило, такое случается при ручном логировании.
        """
        success = kwargs.get('success')
        if success is None:
            return 'UNKNOWN'
        if success == True:
            return 'SUCCESS'
        return 'ERROR'

    @staticmethod
    def auto(**kwargs):
        """
        Метка, является ли запись автоматической, то есть сделана ли она через декоратор.
        """
        result = 'AUTO' if kwargs.get('auto') else 'MANUAL'
        return result

    @classmethod
    def function(cls, **kwargs):
        """
        В этом поле выводятся данные из 3-х полей: названия функции, названия модуля и названия сервиса.

        Формат вывода:
        "where: service_name.module.function_name()"

        ВАЖНО: для каждой функции проводится проверка, является она "отдельно стоящей" или является частью класса. Для этого импортируется модуль и у него проверяется наличие атрибута с нужным именем функции. Если атрибут не найдет, или он не является функцией, проверяются классы, объявленные в модуле. Если каждого класса ищется метод с именем функции. Если находится, здесь выводится путь в несколько модифицированном виде:
        "where: service_name.module.ClassName.function_name()"

        Ввиду особенности механизма поиска названия класса, его легко обмануть. Самый простой способ - расположить в одном файле функцию с каким-то именем, и там же разместить класс с методом, где имя такое же. Если вызвать метод, в лог имя класса не запишется.

        Ручные логи, где не указывалось место действия, будут отображены в усеченном виде:
        "where: service_name.?"
        """
        function = kwargs.get('function')
        module = kwargs.get('module')
        service = SettingsStore.service_name
        if (function is not None) and (module is not None):
            function = cls.search_function_name(function, module)
            result = f'where: {service}.{module}.{function}()'
            return result
        elif function is not None:
            result = f'where: {service}.{function}()'
            return result
        return f'where: {service}.?'

    @classmethod
    def search_function_name(cls, function_name, module_name):
        """
        Здесь происходит сканирование модуля с именем module_name в поисках функции с именем function_name.
        Если нашлось - возвращается имя функции. Иначе - ищется класс с методом, который называется так же. Если нашелся, вернется имя ИмяКласса.имя_функции.

        Результат сканирования кэшируется!
        Второй раз для того же набора имени модуля / имени функции сканирование не проводится, результат берется из кэша.
        """
        key = (function_name, module_name)
        if key in cls.FULL_FUNCTIONS_NAMES:
            return cls.FULL_FUNCTIONS_NAMES[key]
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            return function_name
        if hasattr(module, function_name):
            maybe_function = getattr(module, function_name)
            if callable(maybe_function):
                cls.FULL_FUNCTIONS_NAMES[key] = function_name
        else:
            new_function_name = None
            for object_name in dir(module):
                _object = getattr(module, object_name)
                if inspect.isclass(_object):
                    if hasattr(_object, function_name):
                        new_function_name = f'{object_name}.{function_name}'
                        break
            if new_function_name is None:
                cls.FULL_FUNCTIONS_NAMES[key] = function_name
            else:
                cls.FULL_FUNCTIONS_NAMES[key] = new_function_name
        return cls.FULL_FUNCTIONS_NAMES[key]

    @classmethod
    def result(cls, **kwargs):
        """
        Возвращается строка с возвращаемым значением функции в человекочитаемом виде.
        Ожидается, что исходное значение - строка с JSON-объектом, у которого 2 ключа: 'type' и 'value'.

        Пример результата:
        'result: 1 (int), "hello" (str), <AnotherClass object> (AnotherClass)'
        """
        if 'result' in kwargs:
            variables = kwargs.get('result')
            if isinstance(variables, str):
                try:
                    variables = json.loads(variables)
                    variables = cls.json_variable_to_human_readable_text(variables)
                    return  f"result: {variables}"
                except ValueError:
                    return f'result: {str(variables)} ({type(variables)})'
            return f'result: {str(variables)} ({type(variables)})'
        return None

    @staticmethod
    def json_variable_to_human_readable_text(json_dict):
        """
        Превращаем переменную, сериализованную в формате JSON, в человекочитаемую.
        На момент передачи в данную функцию JSON-документ должен быть уже десериализован.

        На вход принимается словарь вида:
        {'value': 1, 'type': 'int'}

        На выходе получится такая строка:
        '1 (int)'

        Значения строковых пременных дополнительно оборачиваются в двойные кавычки:
        {'value': 'hello', 'type': 'str'} -> '"hello" (str)'
        """
        value = json_dict.get('value')
        _type = json_dict.get('type')
        value = f'"{value}"' if _type == 'str' else value
        result = f'{value} ({_type})'
        return result

    @classmethod
    def json_variables_to_text(cls, json_text):
        """
        Преобразуем перечисление аргументов функции из формата JSON в человекочитаемый вид.

        На вход получаем строку с документом в формате JSON следующей структуры:
        {'args': [{'value': 1, 'type': 'int'}, ...], 'kwargs': {'var_name_1': {'value': 3, 'type': 'int'}, ...}}

        На выходе будет строка вида:
        '1 (int), var_name_1 = 3 (int)'

        Допускается отсутствие блоков 'args' или 'kwargs' в исходном JSON-документе.
        """
        if json_text is None:
            return None
        if not json_text:
            return None
        json_dict = json.loads(json_text)
        args = json_dict.get('args')
        kwargs = json_dict.get('kwargs')
        if args is None and kwargs is None:
            return None
        result = []
        if args is not None:
            args = ', '.join([cls.json_variable_to_human_readable_text(x) for x in args])
            result.append(args)
        if kwargs is not None:
            kwargs = ', '.join([f'{x} = {cls.json_variable_to_human_readable_text(y)}' for x, y in kwargs.items()])
            result.append(kwargs)
        result = ', '.join(result)
        return result

    @classmethod
    def input_variables(cls, **kwargs):
        """
        Преобразуем в человекочитаемый вид строку JSON с аргументами функции.
        """
        variables = kwargs.get('input_variables')
        result = cls.json_variables_to_text(variables)
        if result is None:
            return result
        result = f'input variables: {result}'
        return result

    @classmethod
    def local_variables(cls, **kwargs):
        """
        Преобразуем в человекочитаемый вид строку JSON с локальными переменными.

        Возможен пользовательский ввод! Соблюдение ожидаемого формата документа JSON гарантируется только в случае автоматических логов.
        """
        variables = kwargs.get('local_variables')
        if variables is None:
            return None
        try:
            result = cls.json_variables_to_text(variables)
            if result is None:
                return result
            result = f'local variables: {result}'
            return result
        except:
            return f'local variables: {variables}'

    @staticmethod
    def time_of_work(**kwargs):
        """
        Время работы функции в формате строки, где оно указывается вещественным числом секунд с точностью до 8 знаков после запятой.
        Все ненужные ноли справа удаляются.
        """
        var = kwargs.get('time_of_work')
        if var is None:
            return None
        number = f'{var:.8f}'
        number = number.rstrip('0.')
        result = f"time of work: {number} sec."
        return result

    @staticmethod
    def exception(**kwargs):
        """
        В "сырых" данных название исключения и его сообщение хранятся в отдельных полях. Здесь мы их склеиваем.
        """
        exception_type = kwargs.get('exception_type')
        exception_message = kwargs.get('exception_message')
        if exception_type is not None and exception_message is not None:
            return f'exception: {exception_type}("{exception_message}")'

    @staticmethod
    def traceback(**kwargs):
        """
        Преобразуем трейсбек, строки которого записаны в JSON-список, в человекочитаемый вид.
        """
        traceback = kwargs.get('traceback')
        if traceback is not None:
            if not traceback:
                return 'no traceback'
            traceback = json.loads(traceback)
            if not traceback:
                return 'no traceback'
            result = []
            for line in traceback:
                splitted_line = line.split()
                path = splitted_line[1]
                line_num = splitted_line[3]
                where = splitted_line[5]
                message = ' '.join(splitted_line[6:])
                result.append(f'{message} ({path} line {line_num} in {where})')
            full_traceback = '; '.join(result)
            full_traceback = f'traceback: {full_traceback}'
            return full_traceback
