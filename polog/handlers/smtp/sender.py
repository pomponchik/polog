import smtplib
import atexit
from email.mime.text import MIMEText


class SMTP_sender:
    """
    Класс-обработчик для логов.
    Объект класса является вызываемым благодаря наличию метода .__call__().
    При вызове объекта данного класса происходит отправка электронного письма через SMTP-протокол. В конструкторе возможно конфигурирование условий, при которых отправка писем не производится.
    """
    def __init__(self, email_from, password, smtp_server, email_to, port=465, text_assembler=None, subject_assembler=None, only_errors=None, filter=None, alt=None, is_html=False):
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
        """
        self.email_from = email_from
        self.password = password
        self.email_to = email_to
        self.port = port
        self.smtp_server = smtp_server
        self.text_assembler = text_assembler
        self.subject_assembler = subject_assembler
        self.filter = filter
        self.only_errors = only_errors
        self.alt = alt
        self.is_html = is_html

    def __call__(self, args, **kwargs):
        """
        Благодаря этой функции объект класса SMTP_sender является вызываемым.
        При вызове происходит отправка электронного письма на сервер через SMTP-протокол.
        В случае неудачи при отправке (например, если учетные данные для сервера были указаны неправильно), выполняется функция alt, если она была указана при инициализации объекта
        """
        if not self.to_send_or_not_to_send(**kwargs):
            return self.run_alt(**kwargs)
        try:
            message = self.get_mime(**kwargs)
            self.send(message)
        except Exception:
            self.run_alt(**kwargs)

    def __repr__(self):
        return f'SMTP_sender(email_from="{self.email_from}", password=<HIDDEN>, smtp_server="{self.smtp_server}", email_to="{self.email_to}", port={self.port}, text_assembler={self.text_assembler}, subject_assembler={self.subject_assembler}, alt={self.alt})'

    def send(self, message):
        """
        Обертка для отправки сообщения.
        При каждой отправке сообщения объект соединения с сервером создается заново.
        """
        self.create_smtp_server()
        self.send_mail(message)
        self.quit_from_server()

    def send_mail(self, message):
        """
        Отправляем сообщение.
        """
        self._server.sendmail(self.email_from, [self.email_to], message.as_string())

    def create_smtp_server(self):
        """
        Создание объекта SMTP-сервера и логин.
        """
        self._server = smtplib.SMTP_SSL(self.smtp_server, self.port)
        self._server.login(self.email_from, self.password)

    def quit_from_server(self):
        """
        Разлогиниваемся на сервере.
        """
        if hasattr(self, '_server'):
            try:
                self._server.quit()
            except:
                pass

    def recreate_smtp_server(self):
        """
        Завершаем соединение с сервером и создаем новое.
        """
        self.quit_from_server()
        self.create_smtp_server()

    def get_mime(self, args, **kwargs):
        """
        Наполнение письма контентом.
        """
        text = self.get_text(**kwargs)
        if self.is_html:
            message = MIMEText(text, "html")
        else:
            message = MIMEText(text)
        message['Subject'] = self.get_subject(args, **kwargs)
        message['From'] = self.email_from
        message['To'] = self.email_to
        return message

    def get_text(self, args, **kwargs):
        """
        Данный метод возвращает текст письма.
        Клиент может передать в конструктор класса собственную функцию, которая принимает в себя те же аргументы, что метод __call__() текущего класса, и возвращает строку. В этом случае результат выполнения данной функции будет использован в теле письма. Иначе текст письма будет сгенерирован по умолчанию.
        """
        if callable(self.text_assembler):
            return self.text_assembler(**kwargs)
        return self.get_standart_text(**kwargs)

    def get_standart_text(self, args, **kwargs):
        """
        Метод, возвращающий текст письма по умолчанию.
        По умолчанию текст письма - это просто перечисление всех переданных в метод __call__() аргументов.
        """
        elements = [f'{key} = {value}' for key, value in kwargs.items()]
        text = '\n'.join(elements)
        if text:
            text = f'Message from the Polog:\n\n{text}'
            return text
        return 'Empty message from the Polog.'

    def get_subject(self, args, **kwargs):
        """
        Данный метод возвращает тему письма.
        По умолчанию берется стандартная тема, однако клиент может кастомизировать создание темы, передав в конструктор класса аргумент "subject_assembler". Это должна быть функция, принимающая те же аргументы, что и метод __call__() текущего класса, и возвращающая строку, которая собственно и будет использована в качестве темы письма.
        """
        if callable(self.subject_assembler):
            return self.subject_assembler(**kwargs)
        return self.get_standart_subject(**kwargs)

    def get_standart_subject(self, args, **kwargs):
        """
        Данный метод вызывается, когда клиент не установил альтернативных обработчиков для генерации темы письма.
        Тема письма генерируется на основании аргумента "success", переданного в метод __call__().
        """
        success = kwargs.get('success')
        if success:
            return 'Success message from the Polog'
        return 'Error message from the Polog'

    def to_send_or_not_to_send(self, args, **kwargs):
        """
        Здесь принимается решение, отправлять письмо или нет.
        По умолчанию письмо будет отправлено в любом случае.
        Если в конструкторе настройка "only_errors" установлена в положение True, письмо не будет отправлено в случае успешного выполнения логируемой операции.
        Когда настройка "only_errors" не препятствует отправке письма, проверяется еще объект filter, переданный в конструктор. По умолчанию этот объект является None и не влияет на отправку письма. Однако, если это функция, то она будет вызвана с теми же аргументами, с которыми изначально был вызван текущий объект класса SMTP_sender. Если она вернет True, письмо будет отправлено, иначе - нет.
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
        Если по какой-то причине отправить письмо не удалось, запускается данный метод.
        По умолчанию он не делает ничего, однако, если в конструктор класса была передана функция в качестве параметра alt, она будет вызвана со всеми аргументами, которые изначально были переданы в __call__().

        К примеру, в качестве параметра alt можно передать другой объект класса SMTP_sender, который будет отправлять письмо с другого почтового сервера или адреса, когда не доступен основной.
        """
        if callable(self.alt):
            return self.alt(**kwargs)
