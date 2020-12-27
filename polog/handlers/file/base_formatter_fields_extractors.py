import inspect
import importlib
import ujson as json
from polog.levels import Levels


class BaseFormatterFieldsExtractors:
    FULL_FUNCTIONS_NAMES = {}

    @staticmethod
    def time(**kwargs):
        return f'[{kwargs.get("time")}]'

    @staticmethod
    def level(**kwargs):
        result = Levels.get_level_name(kwargs.get('level'))
        return result

    @staticmethod
    def message(**kwargs):
        result = kwargs.get('message', None)
        if result is None:
            return None
        result = f'"{result}"'
        return result

    @staticmethod
    def success(**kwargs):
        result = 'SUCCESS' if kwargs.get('success') else 'ERROR'
        return result

    @staticmethod
    def auto(**kwargs):
        result = 'AUTO' if kwargs.get('auto') else 'MANUAL'
        return result

    @classmethod
    def function(cls, **kwargs):
        function = kwargs.get('function', None)
        module = kwargs.get('module', None)
        service = kwargs.get('service_name', None)
        if (function is not None) and (module is not None):
            function = cls.search_function_name(function, module)
            result = f'where: {service}.{module}.{function}()'
            return result
        return f'where: {service}.?'

    @classmethod
    def search_function_name(cls, function_name, module_name):
        key = (function_name, module_name)
        if key in cls.FULL_FUNCTIONS_NAMES:
            return cls.FULL_FUNCTIONS_NAMES[key]
        module = importlib.import_module(module_name)
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
        if 'result' in kwargs:
            variables = kwargs.get('result')
            variables = json.loads(variables)
            variables = cls.json_variable_to_human_readable_text(variables)
            result = f"result: {variables}"
            return result
        return None

    @staticmethod
    def json_variable_to_human_readable_text(json_dict):
        value = json_dict.get('value')
        _type = json_dict.get('type')
        value = f'"{value}"' if _type == 'str' else value
        result = f'{value} ({_type})'
        return result

    @classmethod
    def json_variables_to_text(cls, json_text):
        if json_text is None:
            return None
        json_dict = json.loads(json_text)
        args = json_dict.get('args', None)
        kwargs = json_dict.get('kwargs', None)
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
        variables = kwargs.get('input_variables')
        result = cls.json_variables_to_text(variables)
        if result is None:
            return result
        result = f'input variables: {result}'
        return result

    @classmethod
    def local_variables(cls, **kwargs):
        variables = kwargs.get('local_variables')
        if variables is None:
            return None
        args = json.loads(variables)
        result = ', '.join([f'{x} = {cls.json_variable_to_human_readable_text(y)}' for x, y in args.items()])
        result = f'local variables: {result}'
        return result

    @staticmethod
    def time_of_work(**kwargs):
        result = f"time of work: {kwargs.get('time_of_work'):.8f} sec." if 'time_of_work' in kwargs else None
        return result
