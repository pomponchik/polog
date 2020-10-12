import os
from pony.orm import Database


class Connector:
    """
    Класс для хранения коннекта к БД.
    """
    def __init__(self, **kwargs):
        """
        Сюда передаются аргументы в соответствии с документацией pony ORM:
        https://docs.ponyorm.org/database.html
        """
        if not len(kwargs):
            kwargs = dict(provider='sqlite', filename=os.path.join(os.getcwd(), 'logs.db'), create_db=True)
        self.args = {**kwargs}
        self.db = Database()

    def __str__(self):
        return f'<Connector to database object #{id(self)}>'

    def __repr__(self):
        get_argument = lambda x: x if type(x) is not str else f'"{x}"'
        args = ', '.join([f'{x}={get_argument(self.args[x])}' for x in self.args])
        repr = f'{self.__class__.__name__}({args})'
        return repr

    def get_db(self):
        return self.db

    def bind(self):
        self.db.generate_mapping(create_tables=True)
        self.db.bind(self.args)
