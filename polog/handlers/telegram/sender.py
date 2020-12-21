from email.mime.text import MIMEText
from polog.handlers.smtp.smtp_dependency_wrapper import SMTPDependencyWrapper
import telebot

class TelegramSender:
    """

    """
    def __init__(self, token, chat_id, alt = None, text_assembler=None, only_errors=None, filter=None):
        """

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
        return f'telegram_sender(message={self.message}, alt={self.alt})'

    def send(self, message):
        """
        инициализирует бота, и отправляет сообщение
        """
        bot = telebot.telebot(self.token)
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
