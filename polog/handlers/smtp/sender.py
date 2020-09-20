import smtplib
from email.mime.text import MIMEText


class SMTP_sender(object):
    """
    Класс-обработчик для логов.
    Объект класса является вызываемым благодаря наличию метода __call__().
    При вызове объекта данного класса происходит отправка электронного письма через SMTP-протокол. В конструкторе возможно конфигурирование условий, при которых отправка писем при вызове не производится.
    """
    def __init__(self, email_from, password, smtp_server, email_to, port=465, text_assembler=None, subject_assembler=None, decider=None, only_errors=None, alt=None):
        self.email_from = email_from
        self.password = password
        self.email_to = email_to
        self.port = port
        self.smtp_server = smtp_server
        self.text_assembler = text_assembler
        self.subject_assembler = subject_assembler
        self.decider = decider
        self.only_errors = only_errors
        self.alt = alt

    def __call__(self, **kwargs):
        if not self.to_send_or_not_to_send(**kwargs):
            return self.run_alt(**kwargs)
        try:
            message = self.get_mime(**kwargs)
            self.send(message)
        except Exception:
            self.run_alt(**kwargs)

    def __repr__(self):
        return f'SMTP_sender(email_from="{self.email_from}", password="{self.password}", smtp_server="{self.smtp_server}", email_to="{self.email_to}", port={self.port}, text_assembler={self.text_assembler}, subject_assembler={self.subject_assembler}, alt={self.alt})'

    def send(self, message):
        server = smtplib.SMTP_SSL(self.smtp_server, self.port)
        server.login(self.email_from, self.password)
        server.sendmail(self.email_from, [self.email_to], message.as_string())
        server.quit()

    def get_mime(self, **kwargs):
        """
        Наполнение письма контентом.
        """
        text = self.get_text(**kwargs)
        message = MIMEText(text)
        message['Subject'] = self.get_subject(**kwargs)
        message['From'] = self.email_from
        message['To'] = self.email_to
        return message

    def get_text(self, **kwargs):
        """
        Данный метод возвращает текст письма.
        Клиент может передать в конструктор класса собственную функцию, которая принимает в себя те же аргументы, что метод __call__() текущего класса, и возвращает строку. В этом случае результат выполнения данной функции будет использован в теле письма. Иначе текст письма будет сгенерирован по умолчанию.
        """
        if callable(self.text_assembler):
            return self.text_assembler(**kwargs)
        return self.get_standart_text(**kwargs)

    def get_standart_text(self, **kwargs):
        """
        Метод, возвращающий текст письма по умолчанию.
        По умолчанию текст письма - это просто перечисление всех переданных в метод __call__() аргументов.
        """
        elements = [f'{key} = {value}' for key, value in kwargs.items()]
        text = '\n'.join(elements)
        if text:
            text = f'Message from the polog:\n\n{text}'
            return text
        return 'Empty message from the polog.'

    def get_subject(self, **kwargs):
        """
        Данный метод возвращает тему письма.
        По умолчанию берется стандартная тема, однако клиент может кастомизировать создание темы, передав в конструктор класса аргумент "subject_assembler". Это должна быть функция, принимающая те же аргументы, что и метод __call__() текущего класса, и возвращающая строку, которая собственно и будет использована в качестве темы письма.
        """
        if callable(self.subject_assembler):
            return self.subject_assembler(**kwargs)
        return self.get_standart_subject(**kwargs)

    def get_standart_subject(self, **kwargs):
        """
        Данный метод вызывается, когда клиент не установил альтернативных обработчиков для генерации темы письма.
        Тема письма генерируется на основании аргумента "success", переданного в метод __call__().
        """
        success = kwargs.get('success')
        if success:
            return 'Success message from the polog'
        return 'Error message from the polog'

    def to_send_or_not_to_send(self, **kwargs):
        """
        Здесь принимается решение, отправлять письмо или нет.
        По умолчанию письмо будет отправлено в любом случае.
        Если в конструкторе настройка "only_errors" установлена в положение True, письмо не будет отправлено в случае успешного выполнения логируемой операции.
        Когда настройка "only_errors" не препятствует отправке письма, проверяется еще объект decider, переданный в конструктор. По умолчанию этот объект является None и не влияет на отправку письма. Однако, если это функция, то она будет вызвана с теми же аргументами, с которыми изначально был вызван текущий объект класса SMTP_sender. Если она вернет True, письмо будет отправлено, иначе - нет.
        """
        if type(self.only_errors) is bool:
            if self.only_errors == True:
                success = kwargs.get('success')
                if success:
                    return False
        if callable(self.decider):
            result = self.decider(**kwargs)
            if type(result) is bool:
                return result
        return True

    def run_alt(self, **kwargs):
        """
        Если по какой-то причине отправить письмо не удалось, запускается данный метод.
        По умолчанию он не делает ничего, однако, если в конструктор класса была передана функция в качестве параметра alt, она будет вызвана со всеми аргументами, которые изначально были переданы в __call__().

        К примеру, в качестве параметра alt можно передать другой объект класса SMTP_sender, который будет отправлять письмо с другого почтового сервера или адреса, когда не доступен основной.
        """
        if callable(self.alt):
            return self.alt(**kwargs)
