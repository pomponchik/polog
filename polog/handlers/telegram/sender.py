import telebot

class TelegramSender:
    """

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


    def __call__(self, args, **kwargs):
        """
        Вызов объекта, в связи с чем происходит проверка на необходимость отправки и отправка сообщения в телеграм
        """
        if not self.to_send_or_not_to_send(args, **kwargs):
            return self.run_alt(args, **kwargs)
        try:
            message = self.get_text(args, **kwargs)
            self.send(message)
        except Exception as e:
            self.run_alt(args, **kwargs)

    def __repr__(self):
        return f'telegram_sender(chat_id={self.chat_id}, alt={self.alt}, text_assembler={self.text_assembler}, only_errors={self.only_errors}, filter={self.filter})'

    def send(self, message):
        """
        инициализирует бота, и отправляет сообщение
        """
        bot = telebot.TeleBot(self.token)
        bot.send_message(self.chat_id, message)

    def get_text(self, args, **kwargs):
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

    def to_send_or_not_to_send(self, args, **kwargs):
        """
        Здесь принимается решение, отправлять сообщение или нет.
        По умолчанию сообщение будет отправлено в любом случае.
        Если в конструкторе настройка "only_errors" установлена в положение True, сообщение не будет отправлено в случае успешного выполнения логируемой операции.
        Когда настройка "only_errors" не препятствует отправке сообщения, проверяется еще объект filter, переданный в конструктор. По умолчанию этот объект является None и не влияет на отправку сообщения. Однако, если это функция, то она будет вызвана с теми же аргументами, с которыми изначально был вызван текущий объект класса SMTP_sender. Если она вернет True, сообщение будет отправлено, иначе - нет.
        """
        if type(self.only_errors) is bool:
            if self.only_errors == True:
                success = kwargs.get('success')
                if success:
                    return False
        if callable(self.filter):
            result = self.filter(**kwargs)
            if type(result) is bool:
                return result
        return True

    def run_alt(self, args, **kwargs):
        """
        Если по какой-то причине отправить сообщение не удалось, запускается данный метод.
        По умолчанию он не делает ничего, однако, если в конструктор класса была передана функция в качестве параметра alt, она будет вызвана со всеми аргументами, которые изначально были переданы в __call__().
        """
        if callable(self.alt):
            return self.alt(args, **kwargs)
