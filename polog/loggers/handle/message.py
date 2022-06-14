from contextvars import ContextVar

from polog.loggers.handle.abstract import AbstractHandleLogger


context = ContextVar('context')


class Message(AbstractHandleLogger):
    """
    При помощи данного класса можно редактировать сообщение и некоторые другие характеристики лога, записываемого через декоратор функций (экземпляр FunctionLogger), изнутри задекорированной функции.
    Для синхронизации с логирующим декоратором используется контекстная переменная.
    """
    _forbidden_fields = {
        'function',
    }

    def _push(self, fields):
        """
        Сохраняем полученные поля в контекстную переменную.

        fields - словарь с данными, извлеченными из переданных пользователем аргументов.
        """
        if fields:
            context.set(fields)

    def _specific_processing(self, fields):
        """
        Извлекаем данные об исключении, если оно было передано.
        Метка success не затрагивается.
        Уровень логирования в случае передачи исключения также автоматически не меняется.

        fields - словарь с данными, извлеченными из переданных пользователем аргументов.
        """
        self._extract_exception(fields, change_success=False, change_level=False)

    def _copy_context(self, old_args):
        """
        Все поля словаря, извлеченного с помощью message, копируются в словарь с аргументами, извлеченными в декораторе автоматически.
        Автоматические значения перезатираются.
        После копирования всех полей, контекст очищается.

        old_args - словарь с данными, уже извлеченными в декораторе.
        """
        new_args = self._get_context()
        if new_args is not None:
            for key, value in new_args.items():
                old_args[key] = value
        self._clean_context()

    def _clean_context(self):
        """
        Обнуляем контекстную переменную.
        """
        context.set(None)

    def _get_context(self):
        """
        Возвращаем содержимое контекстной переменной.
        Значение по умолчанию - None.
        """
        return context.get(None)


message = Message()
