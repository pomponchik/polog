class LogItem:
    """
    Представление лога в памяти.
    Используется, чтобы не хранить логи в виде каких-то абстрактных списков или словарей.
    """
    def __init__(self, args, **kwargs):
        """
        Сюда передаются "сырые" данные лога.
        """
        self.args = args[0]
        self.kwargs = args[1]
        self.fields = {**kwargs}

    def __getitem__(self, key):
        """
        Возвращаем содержимое полей по ключу.
        """
        return self.fields[key]
