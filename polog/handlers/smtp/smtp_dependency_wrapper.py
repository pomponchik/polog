import smtplib


class SMTPDependencyWrapper:
    """
    Политика отправки сообщений в Polog отделена от реализации.
    Данный класс представляет реализацию, т. е. низкоуровневые методы для работы с SMTP-протоколом.
    Это необходимо, чтобы класс с политикой был тестируемым.
    """
    def __init__(self, server, port, email_from, password, email_to):
        self.server = server
        self.port = port
        self.email_from = email_from
        self.password = password
        self.email_to = email_to

    def send(self, message):
        """
        Обертка для отправки сообщения.
        При каждой отправке сообщения объект соединения с сервером создается заново.
        """
        self.create_smtp_server()
        self.send_mail(message)
        self.quit_from_server()

    def create_smtp_server(self):
        """
        Создание объекта SMTP-сервера и логин.
        """
        self._server = smtplib.SMTP_SSL(self.server, self.port)
        self._server.login(self.email_from, self.password)

    def send_mail(self, message):
        """
        Отправляем сообщение.
        """
        self._server.sendmail(self.email_from, [self.email_to], message.as_string())

    def quit_from_server(self):
        """
        Разлогиниваемся на сервере.
        """
        if hasattr(self, '_server'):
            try:
                self._server.quit()
            except:
                pass
