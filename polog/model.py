import datetime
from pony.orm import Required, PrimaryKey, Optional
from polog.db import db
from polog.base_settings import BaseSettings


class Log(db.Entity):
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
