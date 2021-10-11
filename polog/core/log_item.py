from dataclasses import dataclass
from functools import total_ordering

from polog.errors import RewritingLogError


@dataclass
class FunctionInputData:
    args: tuple = None
    kwargs: dict = None


@total_ordering
class LogItem:
    """
    Каждый экземпляр класса соответствует единичному зафиксированному событию (т. е. логу).

    Логи передаются в обработчики и уже там каким-то образом обрабатываются, например сохраняются в файл или отправляются на сторонний сервер. При этом коллекция обработчиков хранится в самом логе. Это нужно, поскольку с логами, полученными из разных мест программы, могут работать разные наборы обработчиков.
    """

    __slots__ = ('_function_input_data', '_handlers', 'fields')

    def __getitem__(self, key):
        """
        Возвращаем содержимое полей по ключу.
        """
        try:
            return self.fields[key]
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        """
        Поднимаем исключение в случае попытки переписать поля лога.

        Это необходимая защита, поскольку иначе один плохо написанный обработчик мог бы аффектить работу остальных.
        """
        raise RewritingLogError('You are trying to change the log. This is forbidden, because it can create a conflict between handlers.')

    def __delitem__(self, key):
        """
        По аналогии с .__setitem__(), поднимаем исключение при попытке удалить значение из лога по ключу.
        """
        raise RewritingLogError('You are trying to change the log. This is forbidden, because it can create a conflict between handlers.')

    def __str__(self):
        """
        Преобразование данных лога в строковое представление.
        """
        content = []
        if not hasattr(self, 'fields') or not self.fields:
            return f'<log item #{id(self)} (empty)>'
        for field_name, value in self.fields.items():
            if isinstance(value, str):
                value = f'"{value}"'
            item = f'{field_name} = {value}'
            content.append(item)
        content = ', '.join(content)
        return f'<log item #{id(self)} with content: {content}>'

    def __iter__(self):
        try:
            return iter(self.fields)
        except AttributeError:
            return iter(())

    def __contains__(self, key):
        try:
            return key in self.fields
        except AttributeError:
            return False

    def __len__(self):
        try:
            return len(self.fields)
        except AttributeError:
            return 0

    def __eq__(self, other):
        if isinstance(other, type(self)):
            ts_1 = self.get('time')
            ts_2 = other.get('time')

            if ts_1 is None or ts_2 is None:
                return False

            if ts_1 == ts_2:
                return True
        return False

    def __lt__(self, other):
        """
        Определяем поведение при использовании оператора '<' ("меньше").

        За счет декоратора @total_ordering поведение данного метода используется при определении поведения и прочих методов сравнения, кроме проверки на равенство.

        В отличие от метода .__eq__(), при сравнении с объектами других типов поднимется TypeError.
        """
        if isinstance(other, type(self)):
            ts_1 = self.get('time')
            ts_2 = other.get('time')

            if ts_1 is None:
                raise TypeError(f'The "time" field is not defined for object \'{ts_1}\'. It is necessary for comparison.')
            elif ts_2 is None:
                raise TypeError(f'The "time" field is not defined for object \'{ts_2}\'. It is necessary for comparison.')

            return ts_1 < ts_2
        raise TypeError(f"'<' not supported between instances of '{type(self)}' and '{type(other)}'")

    def items(self):
        try:
            return self.fields.items()
        except AttributeError:
            return ()

    def keys(self):
        try:
            return self.fields.keys()
        except AttributeError:
            return ()

    def values(self):
        try:
            return self.fields.values()
        except AttributeError:
            return ()

    @property
    def function_input_data(self):
        if hasattr(self, '_function_input_data'):
            return self._function_input_data
        return FunctionInputData()

    @function_input_data.setter
    def function_input_data(self, value):
        if not isinstance(value, FunctionInputData):
            raise ValueError('Incorrect data type of the value.')
        self._function_input_data = value

    def get(self, key, *default):
        try:
            return self.fields.get(key, *default)
        except AttributeError:
            return {}.get(key, *default)

    def set_data(self, data):
        self.fields = data

    def set_function_input_data(self, args, kwargs):
        """
        Сюда передаются данные, полученные функцией в качестве аргументов.

        Это может работатать примерно так:

        >>> def func(*args, **kwargs):
        ...    log = LogItem()
        ...    log.set_function_input_data(args, kwargs)
        ...    return log

        То есть args и kwargs - это, соответственно, кортеж и словарь с позиционными и именованными аргументами функции.
        Обработчики могут использовать эти данные только в редких случаях и на свой страх и риск, поскольку существует возможность повредить данные функции.
        """
        self.function_input_data = FunctionInputData(args=args, kwargs=kwargs)

    def set_handlers(self, handlers):
        pass
