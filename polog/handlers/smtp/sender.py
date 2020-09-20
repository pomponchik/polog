import smtplib
from email.mime.text import MIMEText


class SMTP_sender(object):
    def __init__(self, email_from, password, smtp_server, email_to, text_assembler=None, subject_assembler=None, decider=None, only_errors=None, alt=None):
        self.email_from = email_from
        self.password = password
        self.email_to = email_to
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
            server = smtplib.SMTP_SSL(self.smtp_server, 465)
            server.login(self.email_from, self.password)
            server.sendmail(self.email_from, [self.email_to], message.as_string())
            server.quit()
        except Exception:
            self.run_alt(**kwargs)

    def get_mime(self, **kwargs):
        text = self.get_text(**kwargs)
        message = MIMEText(text)
        message['Subject'] = self.get_subject(**kwargs)
        message['From'] = self.email_from
        message['To'] = self.email_to
        return message

    def get_text(self, **kwargs):
        if callable(self.text_assembler):
            return self.text_assembler(**kwargs)
        return self.get_standart_text(**kwargs)

    def get_standart_text(self, **kwargs):
        elements = [f'{key} = {value}' for key, value in kwargs.items()]
        text = '\n'.join(elements)
        if text:
            text = f'Message from the polog:\n\n{text}'
            return text
        return 'Empty message from the polog.'

    def get_subject(self, **kwargs):
        if callable(self.subject_assembler):
            return self.subject_assembler(**kwargs)
        return self.get_standart_subject(**kwargs)

    def get_standart_subject(self, **kwargs):
        success = kwargs.get('success')
        if success:
            return 'Success message from the polog'
        return 'Error message from the polog'

    def to_send_or_not_to_send(self, **kwargs):
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
        if callable(self.alt):
            return self.alt(**kwargs)
