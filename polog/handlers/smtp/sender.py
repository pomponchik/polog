from email.mime.text import MIMEText

from polog.core.utils.signature_matcher import SignatureMatcher
from polog.handlers.abstract.base import BaseHandler
from polog.handlers.smtp.smtp_dependency_wrapper import SMTPDependencyWrapper


class SMTP_sender(BaseHandler):
    """
    Класс-обработчик для логов.
    Объект класса является вызываемым благодаря наличию метода .__call__().
    При вызове объекта данного класса происходит отправка электронного письма через SMTP-протокол. В конструкторе возможно конфигурирование условий, при которых отправка писем не производится.
    """

    input_proves = {
        'email_from': lambda x: isinstance(x, str),
        'password': lambda x: isinstance(x, str),
        'email_to': lambda x: isinstance(x, str),
        'port': lambda x: isinstance(x, int),
        'smtp_server': lambda x: isinstance(x, str),
        'text_assembler': lambda x: x is None or SignatureMatcher.is_handler(x),
        'subject_assembler': lambda x: x is None or SignatureMatcher.is_handler(x),
        'is_html': lambda x: isinstance(x, bool),
    }

    def __init__(self, email_from, password, smtp_server, email_to, port=465, text_assembler=None, subject_assembler=None, only_errors=False, filter=None, alt=None, is_html=False, smtp_wrapper=SMTPDependencyWrapper):
        """
        Здесь происходит конфигурирование отправщика писем.

        Обязательные аргументы:
        email_from (str) - адрес электронной почты, с которого должна происходить отправка писем.
        password (str) - пароль для почтового ящика, соответствующего адресу "email_from".
        smtp_server (str) - адрес сервера, через который происходит отправка почты.
        email_to (str) - адрес электронной почты, на который происходит отправка писем.

        Необязательные аргументы:
        port (int) - номер порта в почтовом сервере, через который происходит отправка почты. По умолчанию 465 (обычно используется для шифрованного соединения).
        text_assembler (function) - альтернативная функция для генерации текста сообщений. Должна принимать в себя те же аргументы, что метод .__call__() текущего класса и возвращать строковый объект.
        subject_assembler (function) - по аналогии с аргументом "text_assembler", альтернативная функция для генерации темы письма. Должна принимать аргументы как .__call__() и возвращать строку.
        only_errors (bool) - фильтр на отправку писем. В режиме False (то есть по умолчанию) через него проходят все события. В режиме True - только ошибки, т. е., если это не ошибка, письмо гарантированно отправлено не будет.
        filter (function) - дополнительный пользовательский фильтр на отправку сообщений. По умолчанию он отсутствует, т. е. отправляются сообщения обо всех событиях, прошедших через фильтр "only_errors" (см. строчкой выше). Пользователь может передать сюда свою функцию, которая должна принимать набор аргументов, аналогичный методу .__call__() текущего класса, и возвращать bool. Возвращенное значение True из данной функции будет означать, что сообщение нужно отправлять, а False - что нет.
        alt (function) - функция, которая будет выполнена в случае, если отправка сообщения не удалась или запрещена фильтрами. Должна принимать тот же набор аргументов, что и метод .__call__() текущего класса. Возвращаемые значения не используются.
        is_html (bool) - флаг, является ли отправляемое содержимое HTML-документом. По умолчанию False.
        smtp_wrapper (SMTPDependencyWrapper или иной тип с аналогичным протоколом) - класс, в котором реализована вся низкоуровневая обвязка для отправки писем по протоколу SMTP. Таким образом класс SMTP_sender становится более тестируемым, поскольку содержит только "политику" отправки писем.
        """
        super().__init__(only_errors=only_errors, filter=filter, alt=alt)
        self.do_input_proves(email_from=email_from, password=password, email_to=email_to, port=port, smtp_server=smtp_server, text_assembler=text_assembler, subject_assembler=subject_assembler, is_html=is_html)
        self.email_from = email_from
        self.password = password
        self.email_to = email_to
        self.port = port
        self.smtp_server = smtp_server
        self.text_assembler = text_assembler
        self.subject_assembler = subject_assembler
        self.is_html = is_html
        self.smtp_wrapper = smtp_wrapper(self.smtp_server, self.port, self.email_from, self.password, self.email_to)

    def __repr__(self):
        return f'SMTP_sender(email_from="{self.email_from}", password=<HIDDEN>, smtp_server="{self.smtp_server}", email_to="{self.email_to}", port={self.port}, text_assembler={self.text_assembler}, subject_assembler={self.subject_assembler}, alt={self.alt})'

    def do(self, message):
        """
        Обертка для отправки сообщения.
        При каждой отправке сообщения объект соединения с сервером создается заново.
        """
        self.smtp_wrapper.send(message)

    def get_content(self, log):
        """
        Наполнение письма контентом.
        """
        text = self.get_text(log)
        if self.is_html:
            message = MIMEText(text, "html")
        else:
            message = MIMEText(text)
        message['Subject'] = self.get_subject(log)
        message['From'] = self.email_from
        message['To'] = self.email_to
        return message

    def get_text(self, log):
        """
        Данный метод возвращает текст письма.
        Клиент может передать в конструктор класса собственную функцию, которая принимает в себя те же аргументы, что метод __call__() текущего класса, и возвращает строку. В этом случае результат выполнения данной функции будет использован в теле письма. Иначе текст письма будет сгенерирован по умолчанию.
        """
        if callable(self.text_assembler):
            return self.text_assembler(log)
        return self.get_standart_text(log)

    def get_standart_text(self, log):
        """
        Метод, возвращающий текст письма по умолчанию.
        По умолчанию текст письма - это просто перечисление всех переданных в метод __call__() аргументов.
        """
        elements = [f'{key} = {value}' for key, value in log.items()]
        text = '\n'.join(elements)
        if text:
            text = f'Message from the Polog:\n\n{text}'
            return text
        return 'Empty message from the Polog.'

    def get_subject(self, log):
        """
        Данный метод возвращает тему письма.
        По умолчанию берется стандартная тема, однако клиент может кастомизировать создание темы, передав в конструктор класса аргумент "subject_assembler". Это должна быть функция, принимающая те же аргументы, что и метод __call__() текущего класса, и возвращающая строку, которая собственно и будет использована в качестве темы письма.
        """
        if callable(self.subject_assembler):
            return self.subject_assembler(log)
        return self.get_standart_subject(log)

    def get_standart_subject(self, log):
        """
        Данный метод вызывается, когда клиент не установил альтернативных обработчиков для генерации темы письма.
        Тема письма генерируется на основании значения по ключу "success" в объекте лога.
        """
        success = log.get('success')
        if success:
            return 'Success message from the Polog'
        elif success is None:
            return 'Message from the Polog'
        return 'Error message from the Polog'
