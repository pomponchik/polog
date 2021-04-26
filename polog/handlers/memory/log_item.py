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
        return self.fields.get(key)

    def __str__(self):
        """
        Выводятся все активные поля лога.
        """
        content = []
        for x, y in self.fields.items():
            if type(y) is str:
                y = f'"{y}"'
            item = f'{x} = {y}'
            content.append(item)
        content = ', '.join(content)
        return f'<log item with content: {content}>'
