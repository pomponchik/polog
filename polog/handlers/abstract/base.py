from abc import abstractmethod
from polog.core.utils.is_handler import is_handler


class BaseHandler:
    """
    Базовый класс обработчика Polog.

    Минимально для создания работоспособного обработчика необходимо переопределить всего 3 метода:

    1. do() - с сохранением сигнатуры.
    2. get_content() - с сохранением сигнатуры.
    3. __init__() - с возможным расширением сигнатуры.
    """

    _input_proves = {
        'only_errors': lambda x: isinstance(x, bool),
        'filter': lambda x: x is None or is_handler(x),
        'alt': lambda x: x is None or is_handler(x),
    }

    def __init__(self, only_errors=False, filter=None, alt=None):
        """
        Образец метода __init__(), переопределение в наследниках обязательно.
        Входные параметры данного метода обязательны для всех наследников, и их необходимо с теми же именами записывать в экземпляр, поскольку от них зависят некоторые методы.
        """
        self.do_input_proves(only_errors=only_errors, filter=filter, alt=alt)
        self.filter = filter
        self.only_errors = only_errors
        self.alt = alt

    def __call__(self, args, **kwargs):
        """
        Благодаря этой функции объект класса является вызываемым.
        В случае неудачи при записи лога, выполняется функция alt, если она была указана при инициализации объекта.
        """
        if not self.to_do_or_not_to_do(args, **kwargs):
            return self.run_alt(args, **kwargs)
        try:
            content = self.get_content(args, **kwargs)
            self.do(content)
        except Exception as e:
            self.run_alt(args, **kwargs)

    def to_do_or_not_to_do(self, args, **kwargs):
        """
        Здесь принимается решение, записывать лог или нет.
        По умолчанию это будет сделано в любом случае.
        Если в конструкторе настройка "only_errors" установлена в положение True, лог не будет записан в случае успешного выполнения логируемой операции.
        Когда настройка "only_errors" не препятствует записи лога, проверяется еще объект filter, переданный в конструктор. По умолчанию этот объект является None и не влияет на запись лога. Однако, если это функция, то она будет вызвана с теми же аргументами, с которыми изначально был вызван текущий объект. Если она вернет True, лог будет записан, иначе - нет.
        """
        if type(self.only_errors) is bool:
            if self.only_errors == True:
                success = kwargs.get('success')
                if success:
                    return False
        if callable(self.filter):
            result = self.filter(args, **kwargs)
            if type(result) is bool:
                return result
        return True

    def run_alt(self, args, **kwargs):
        """
        Если по какой-то причине записать лог не удалось, запускается данный метод.
        По умолчанию он не делает ничего, однако, если в конструктор класса была передана функция в качестве параметра alt, она будет вызвана со всеми аргументами, которые изначально были переданы в __call__().
        К примеру, в качестве параметра alt можно передать другой обработчик.
        """
        if callable(self.alt):
            return self.alt(args, **kwargs)

    @abstractmethod
    def do(self, content):
        """
        Здесь происходит "магия" - лог записывается или отправляется куда-то.
        Подразумевается, что content - уже полностью подготовленный и обработанный объект с данными (обычно строка, но не обязательно).

        Рекомендуем отделить класс, непосредственно работающий с низкоуровневым механизмом записи / отправки логов, от класса, унаследованного от BaseHandler, и здесь вызывать только какой-то его метод.
        """
        pass # pragma: no cover

    @abstractmethod
    def get_content(self, args, **kwargs):
        """
        Метод, который возвращает объект, с которым что-то будет делать self.do().
        В большинстве реализаций обработчиков это будет специфически отформатированная строка.
        """
        pass # pragma: no cover

    def do_input_proves(self, **kwargs):
        """
        Здесь происходит проверка параметров обработчика.

        Функции, которые применяются к аргументам, находятся в словаре self._input_proves. Если любая из них вернет False, значит проверка не пройдена и создать обработчик не получится.
        В отнаследованном классе пользователь может определить словарь self.input_proves, содержащий функции для проверки прочих аргументов.
        """
        if hasattr(self, 'input_proves'):
            input_proves = {**self._input_proves, **self.input_proves}
        else:
            input_proves = {**self._input_proves}
        for key, value in kwargs.items():
            if key in input_proves:
                prove = input_proves[key]
                if not prove(value):
                    raise ValueError(f'The argument "{key}" does not pass the test. Please check its format. If necessary, refer to the documentation for the handler.')
