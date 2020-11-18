from contextvars import ContextVar
from polog.log import ALLOWED_TYPES, CONVERT_VALUES
from polog.utils.exception_to_dict import exception_to_dict
from polog.utils.get_traceback import get_traceback, get_locals_from_traceback


context = ContextVar('context')

class Message:
    def __call__(self, *text, level=None, success=None, e=None, exception=None, exception_type=None, exception_message=None, local_variables=None):
        vars = {}
        if text:
            self.set_var('message', str(text[0]), vars)
        self.set_var('level', level, vars)
        self.set_var('success', success, vars)
        self.set_var('local_variables', local_variables, vars)
        self.extract_exception(e, exception, exception_type, exception_message, vars)
        if vars:
            context.set(vars)

    def copy_context(self, old_args):
        new_args = self.get_context()
        if new_args is not None:
            for key, value in new_args.items():
                old_args[key] = value

    def clean_context(self):
        context.set(None)

    def extract_exception(self, e, exception, exception_type, exception_message, vars):
        new_e = None
        if e is not None and isinstance(e, Exception):
            new_e = e
        elif exception is not None and isinstance(exception, Exception):
            new_e = exception
        if new_e is not None:
            exception_to_dict(vars, e)
            vars['traceback'] = get_traceback()
            vars['local_variables'] = get_locals_from_traceback()
        else:
            if isinstance(exception_type, str):
                vars['exception_type'] = exception_type
            if isinstance(exception_message, str):
                vars['exception_message'] = exception_message

    def set_var(self, name, var, vars, not_none=True):
        if not not_none or var is not None:
            if not ALLOWED_TYPES[name](var):
                raise ValueError(f'Type "{type(var).__name__}" is not allowed for variable "{name}".')
            converter = CONVERT_VALUES.get(name)
            if converter is not None:
                var = converter(var)
            vars[name] = var

    def get_context(self):
        result = context.get(None)
        return result

message = Message()
