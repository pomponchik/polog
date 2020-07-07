import os
from polog.db import db


class Connector(object):
    """
    Класс для хранения коннекта к БД, singleton.
    """
    def __init__(self, **kwargs):
        """
        Сюда передаются аргументы в соответствии с документацией pony ORM:
        https://docs.ponyorm.org/database.html
        """
        if not hasattr(self, 'db'):
            if not len(kwargs):
                kwargs = dict(provider='sqlite', filename=os.path.join(os.getcwd(), 'logs.db'), create_db=True)
            self.args = {**kwargs}
            self.db = db
            self.db.bind(**kwargs)
            self.db.generate_mapping(create_tables=True)

    def __new__(cls, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Connector, cls).__new__(cls)
        return cls.instance

    def __str__(self):
        return f'<Connector to database object #{id(self)}>'

    def __repr__(self):
        get_argument = lambda x: x if type(x) is not str else f'"{x}"'
        args = ', '.join([f'{x}={get_argument(self.args[x])}' for x in self.args])
        repr = f'{self.__class__.__name__}({args})'
        return repr
