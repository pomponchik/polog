from contextvars import ContextVar
from polog.log import ALLOWED_TYPES, CONVERT_VALUES
from polog.utils.exception_to_dict import exception_to_dict
from polog.utils.get_traceback import get_traceback, get_locals_from_traceback


context = ContextVar('context')

class Message:
    """
    При помощи данного класса можно редактировать сообщение и некоторые другие характеристики лога, записываемого через flog(), изнутри задекорированной функции.
    """
    def __call__(self, *text, level=None, success=None, e=None, exception=None, exception_type=None, exception_message=None, local_variables=None):
        """
        При каждом вызове ообъекта класса Message происходит сохранение переданного сюда набора аргументов в словарь, а также сохранение этого словаря в контекстную переменную.

        Первым и единственным опциональным неименованным аргументом идет сообщение (message) лога.
        Остальные аргументы - именнованные:

        level (str, int) - уровень лога.
        success (bool) - метка успешности операции.
        e, exception (Exception) - экземпляр исключения. Можно передать, используя любой из этих ярлыков. Если передать по экземпляру исключения в каждый ярлык, приоритет будет у 'e'.
        exception_type, exception_message (str) - строки с названием класса исключения и его сообщением. Если заполнены аргументы e или exception, содержимое данных аргументов игнорируется.
        local_variables (str) - ожидается строка с перечислением переменных функции в формате json, полученная с помощью json_vars().
        """
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
        """Все поля словаря, извлеченного с помощью message, копируются в словарь с аргументами, извлеченными в декораторе автоматически. Автоматические значения перезатираются."""
        new_args = self.get_context()
        if new_args is not None:
            for key, value in new_args.items():
                old_args[key] = value

    def clean_context(self):
        """Обнуляем контекстную переменную."""
        context.set(None)

    def extract_exception(self, e, exception, exception_type, exception_message, vars):
        """
        Пользователь может передать в message() как как сам экземпляр исключения, так и его текстовое описание.
        ВАЖНО: если в задекорированной функции сначала был передан экземпляр исключения в message(), а потом случилось другое необработанное исключение, последнее залогировано через декоратор не будет, т. к. message() перезаписывает информацию в декораторе.

        Экземпляр исключения можно передать в виде именованных аргументов 'e' или 'exception'. Из него будет автоматически извлечено название класса исключения и сообщение. Если пользователь передал исключение и туда и туда, приоритет будет у 'e'.
        ВАЖНО: в этом случае метка 'success' не затрагивается, т. к. имеется ввиду, что, если исключение ловится внутри функции, оно, вероятно, было ожидаемым и должно быть корректно обработано программой. При необходимости, пользователь может выставить ее в положение False вручную.

        Если экземпляр исключения передан не был, проверяются именованные аргументы 'exception_type' и 'exception_message'. Они должны быть строками. 'exception_type' - это название класса исключения, а 'exception_message' - сообщение, с которым оно было вызвано.
        ВАЖНО: если в message() был передан экземпляр исключения и 'exception_type' / 'exception_message', последние будут проигнорированы, вся информация будет извлечена из самого экземпляра исключения.
        """
        new_e = None
        if e is not None and isinstance(e, Exception):
            new_e = e
        elif exception is not None and isinstance(exception, Exception):
            new_e = exception
        if new_e is not None:
            exception_to_dict(vars, new_e)
            vars['traceback'] = get_traceback()
            vars['local_variables'] = get_locals_from_traceback()
        else:
            if isinstance(exception_type, str):
                vars['exception_type'] = exception_type
            if isinstance(exception_message, str):
                vars['exception_message'] = exception_message

    def set_var(self, name, var, vars, not_none=True):
        """
        Сохраняем переданный пользователем объект в контекстную переменную. При условии, объект ожидаемого типа. При необходимости, конвертируем в нужный тип.
        """
        if not not_none or var is not None:
            if not ALLOWED_TYPES[name](var):
                raise ValueError(f'Type "{type(var).__name__}" is not allowed for variable "{name}".')
            converter = CONVERT_VALUES.get(name)
            if converter is not None:
                var = converter(var)
            vars[name] = var

    def get_context(self):
        """Возвращаем содержимое контекстной переменной. Значение по умолчанию - None."""
        result = context.get(None)
        return result

message = Message()
