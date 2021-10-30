from polog.handlers.file.rotation.rules.rules.tokenization.tokenizator import Tokenizator


class AbstractRule:
    """
    Абстрактный класс, все правила ротации должны быть отнаследованы от него.
    Благодаря такой компоновке добавлять в систему новые правила становится гораздо проще, нужно всего лишь переопределить несколько методов.

    Правило ротации - это некий класс, экземпляр которого перед каждой записью лога должен решать, нужна сейчас ротация или нет.
    Правила могут быть самыми разными. Одни будут смотреть на размер файла, другие на то, когда была произведена последняя ротация, и т. д.
    Интерфейс у всех правил должен быть одинаковым. Если хотя бы одно правило требует ротации, она будет произведена. Если ротации требуют 2 и более правил, она будет проведена 1 раз.

    Правила ротации пользователь задает в виде обычного текста в определенном формате. Этот текст "скармливается" правилу ротации, после чего оно может определить, подходит он по формату или нет.

    Для упрощения парсинга правил ротации из текста в Polog реализованы собственные движки для токенизации текста и обработки высокоуровневых регулярных выражений.
    """
    def __init__(self, source, file):
        self.source = source
        self.file = file
        self.tokens = self.get_tokens(source)
        if self.prove_source():
            self.extract_data_from_string()

    def __repr__(self):
        type_name = type(self).__name__
        source = self.source
        result = f'{type_name}("{source}")'
        return result

    def get_tokens(self, source):
        """
        Получаем группу токенов.
        """
        tokens = Tokenizator(source).generate_tokens()
        return tokens

    def extract_data_from_string(self):
        """
        Эта функция не должна ничего возвращать, она сохраняет извлеченные из исходной строки данные в объект класса сама.
        """
        raise NotImplementedError

    def prove_source(self):
        """
        Здесь мы проверяем, что исходная строка в нужном нам формате, то есть описывает тот тип правил, который обрабатывается конкретным наследником данного класса.
        """
        raise NotImplementedError

    def check(self):
        """
        Эта функция будет вызываться при каждой записи лога.
        Ее задача - определить, должно ли данное правило сработать сейчас.
        """
        raise NotImplementedError
