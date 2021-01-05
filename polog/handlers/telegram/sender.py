import telebot

class TelegramSender(BaseHandler):
    """
    Класс-обработчик для логов.
    Объект класса является вызываемым благодаря наличию метода __call__() в базовом классе
    При вызове объекта данного класса происходит отправка сообщения в телеграм.
    В конструкторе возможно конфигурирование условий, при которых отправка сообщения не производится.
    """
    def __init__(self, token, chat_id, alt=None, text_assembler=None, only_errors=None, filter=None):
        """
        создание объекта отправки сообщение от телеграм-бота

        Обязательные аргументы:
        token (str) - токен полученный от FatherBot для инициализации бота который отсылает сообщения с логами.
        chat_id (int) -  id чата (пользователя телеграм) куда отсылать сообщение.

        Необязательные аргументы:
        text_assembler (function) - альтернативная функция для генерации текста сообщений. Должна принимать в себя те же аргументы, что метод .__call__() текущего класса и возвращать строковый объект.
        only_errors (bool) - фильтр на отправку писем. В режиме False (то есть по умолчанию) через него проходят все события. В режиме True - только ошибки, т. е., если это не ошибка, письмо гарантированно отправлено не будет.
        filter (function) - дополнительный пользовательский фильтр на отправку сообщений. По умолчанию он отсутствует, т. е. отправляются сообщения обо всех событиях, прошедших через фильтр "only_errors" (см. строчкой выше). Пользователь может передать сюда свою функцию, которая должна принимать набор аргументов, аналогичный методу .__call__() текущего класса, и возвращать bool. Возвращенное значение True из данной функции будет означать, что сообщение нужно отправлять, а False - что нет.
        alt (function) - функция, которая будет выполнена в случае, если отправка сообщения не удалась или запрещена фильтрами. Должна принимать тот же набор аргументов, что и метод .__call__() текущего класса. Возвращаемые значения не используются.
        """
        self.token = token
        self.chat_id = chat_id
        self.alt = alt
        self.text_assembler = text_assembler
        self.filter = filter
        self.only_errors = only_errors

    def __repr__(self):
        return f'telegram_sender(chat_id={self.chat_id}, alt={self.alt}, text_assembler={self.text_assembler}, only_errors={self.only_errors}, filter={self.filter})'

    def do(self, content):
        """
        инициализирует бота, и отправляет сообщение в телеграм.
        content - уже полностью подготовленная и обработанная строка
        """
        bot = telebot.TeleBot(self.token)
        bot.send_message(self.chat_id, content)


    def get_content(self, args, **kwargs):
        """
        получает сообщение
        """
        if callable(self.text_assembler):
            return self.text_assembler(args, **kwargs)
        return self.get_standart_text(args, **kwargs)

    def get_standart_text(self, args, **kwargs):
        """
        Метод, возвращающий текст сообщения по умолчанию.
        По умолчанию текст сообщения - это просто перечисление всех переданных в метод __call__() аргументов.
        """
        elements = [f'{key} = {value}' for key, value in kwargs.items()]
        text = '\n'.join(elements)
        if text:
            text = f'Message from the Polog:\n\n{text}'
            return text
        return 'Empty message from the Polog.'
