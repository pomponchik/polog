import datetime
from pony.orm import Required, PrimaryKey, Optional, db_session, commit
from polog.base_settings import BaseSettings
from polog.handlers.pony.connector import Connector


class pony_writer:
    """
    Класс-обработчик для логов.
    Объект класса является вызываемым благодаря наличию метода .__call__().
    При вызову объекта данного класса происходит запись в базу данных.
    """
    def __init__(self, table=None, **kwargs):
        self.table = table if not (table is None) else 'logs'
        self.connector = Connector(**kwargs)
        self.db = self.connector.get_db()
        self.model = self.get_model()
        self.connector.bind()

    @db_session
    def __call__(self, *args, **kwargs):
        log = self.model(**kwargs)
        commit()

    def get_model(self):
        class Log(self.db.Entity):
            _table_ = self.table
            id = PrimaryKey(int, auto=True)
            level = Required(int)
            function = Optional(str)
            module = Optional(str)
            message = Optional(str)
            exception_type = Optional(str)
            exception_message = Optional(str)
            traceback = Optional(str)
            input_variables = Optional(str)
            local_variables = Optional(str)
            result = Optional(str)
            success = Optional(bool)
            time = Required(datetime.datetime)
            time_of_work = Optional(float)
            service = Optional(str)
            auto = Required(bool)
        def __init__(self, **kwargs):
            service = BaseSettings().service_name
            super(Log, self).__init__(**kwargs, service=service)
        Log.__init__ = __init__
        return Log
