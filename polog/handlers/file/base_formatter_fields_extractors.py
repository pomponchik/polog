import inspect
import importlib

from polog.core.stores.levels import Levels
from polog.core.stores.settings.settings_store import SettingsStore


class BaseFormatterFieldsExtractors:
    """
    Данный класс - хранилище функций, преобразующих исходные данные логов в строки нужного формата.

    Если метод возвращает None, поле не выводится в итоговую запись лога.
    """

    settings = SettingsStore()

    @staticmethod
    def time(log):
        """
        Выводим дату и время в квадратных скобках.
        """
        time = log.get("time")
        if time is None:
            return '[----time not specified----]'
        return f'[{time}]'

    @staticmethod
    def level(log):
        """
        Выводим уровень лога. Если присвоено название - выводим его, иначе число.

        Важно: если одному уровню логирования присвоено несколько имен, выводится последнее из них.
        """
        level = log.get('level')
        if level is None:
            return 'UNKNOWN'
        result = Levels.get_level_name(level)
        return result

    @staticmethod
    def message(log):
        """
        Выводим пользовательский комментарий к логу в двойных кавычках.
        """
        result = log.get('message')
        if result is None:
            return None
        result = f'"{result}"'
        return result

    @staticmethod
    def success(log):
        """
        Выводим метку успешности операции.

        Существуют 3 опции успешности: 'SUCCESS', 'ERROR' и 'UNKNOWN'.
        Последний вариант присваивается в том случае, если информации об успешности операции нет.
        Как правило, такое случается при ручном логировании.
        """
        success = log.get('success')
        if success is None:
            return 'UNKNOWN'
        if success == True:
            return 'SUCCESS'
        return 'ERROR'

    @staticmethod
    def auto(log):
        """
        Метка, является ли запись автоматической, то есть сделана ли она через декоратор.
        """
        result = 'AUTO' if log.get('auto') else 'MANUAL'
        return result

    @classmethod
    def function(cls, log):
        """
        В этом поле выводятся данные из 4-х полей: названия функции, названия модуля, названия класса и названия сервиса.

        Формат вывода:
        "where: service_name.module_name.class_name.function_name()"

        Ручные логи, где не указывалось место действия, будут отображены в усеченном виде, например:
        "where: service_name.?"
        """
        function_name = log.get('function')
        class_name = log.get('class')
        module_name = log.get('module')
        service_name = SettingsStore()['service_name']

        if function_name is not None:
            result = '.'.join([x for x in (service_name, module_name, class_name, function_name) if x is not None])
            return f'where: {result}()'
        
        result = '.'.join([x for x in (service_name, module_name, class_name) if x is not None])
        if result:
            return f'where: {result}.?'
        return 'where: ?'

    @classmethod
    def result(cls, log):
        """
        Возвращается строка с возвращаемым значением функции в человекочитаемом виде.
        Ожидается, что исходное значение - строка с JSON-объектом, у которого 2 ключа: 'type' и 'value'.

        Пример результата:
        'result: 1 (int), "hello" (str), <AnotherClass object> (AnotherClass)'
        """
        json = cls.settings['json_module']
        if 'result' in log:
            variables = log.get('result')
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
        json = cls.settings['json_module']
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
    def input_variables(cls, log):
        """
        Преобразуем в человекочитаемый вид строку JSON с аргументами функции.
        """
        variables = log.get('input_variables')
        result = cls.json_variables_to_text(variables)
        if result is None:
            return result
        result = f'input variables: {result}'
        return result

    @classmethod
    def local_variables(cls, log):
        """
        Преобразуем в человекочитаемый вид строку JSON с локальными переменными.

        Возможен пользовательский ввод! Соблюдение ожидаемого формата документа JSON гарантируется только в случае автоматических логов.
        """
        variables = log.get('local_variables')
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
    def time_of_work(log):
        """
        Время работы функции в формате строки, где оно указывается вещественным числом секунд с точностью до 8 знаков после запятой.
        Все ненужные ноли справа удаляются.
        """
        var = log.get('time_of_work')
        if var is None:
            return None
        number = f'{var:.8f}'
        number = number.rstrip('0.')
        result = f"time of work: {number} sec."
        return result

    @staticmethod
    def exception(log):
        """
        В "сырых" данных название исключения и его сообщение хранятся в отдельных полях. Здесь мы их склеиваем.
        """
        exception_type = log.get('exception_type')
        exception_message = log.get('exception_message')
        if exception_type is not None and exception_message is not None:
            return f'exception: {exception_type}("{exception_message}")'

    @classmethod
    def traceback(cls, log):
        """
        Преобразуем трейсбек, строки которого записаны в JSON-список, в человекочитаемый вид.
        """
        json = cls.settings['json_module']
        traceback = log.get('traceback')
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
