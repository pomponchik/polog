import os
import datetime
from threading import Lock
from multiprocessing import current_process

from polog.handlers.file.rotation.parser import Parser


class Rotator:
    """
    Здесь происходит все, что связано с ротацией логов:

    1. Извлекаются правила ротации из переданной пользователем строки.
    2. Принимается решение, нужно в данный момент ротировать файл с логами или нет. Оно основано на извлеченных правилах - если сработало хотя бы одно из них, ротация случится.
    3. Принимается решение, куда перемещать файл с логами.
    4. Осуществляется собственно ротация.
    """

    def __init__(self, source_string, file, parser=Parser):
        if source_string and file.filename is None:
            raise ValueError('Rotation is not possible when logs are not output to a file.')
        self.file = file
        self.parser = parser(self.file)
        self.source_rules = self.extract_rules_string_from_source(source_string)
        self.to = self.where_to_rotate(source_string)
        self.rules = self.generate_rules(self.source_rules)
        self.lock = Lock()

    def maybe_do(self):
        """
        Определяем, нужно ли ротировать файл с логами, и если да - вызываем команду ротации.
        """
        # Лок для защиты от состояния гонки, т. к. необходимость ротации могут одновременно проверять несколько потоков.
        # Если не защитить, ротация может дублироваться из разных потоков.
        with self.lock:
            if self.to_do_or_not_to_do():
                self.do()

    def to_do_or_not_to_do(self):
        """
        Здесь принимается решение, нужно ли в данный момент ротировать файл с логами.
        """
        for rule in self.rules:
            if rule.check():
                return True
        return False

    def do(self):
        """
        Копируем файл с логами в указанную пользователем папку, переоткрываем файл по старому пути.
        В качестве нового имени файла используем название файла корневого скрипта, с измененным на .log расширением и суффиксом, отображающим текущую дату и время.
        """
        self.file.move_file(os.path.join(self.to, self.new_filename()))

    def generate_rules(self, source_rules):
        """
        Берем строку с правилами ротации и возвращаем список объектов правил.
        """
        if source_rules is None:
            return []
        rules = self.parser.extract_rules(source_rules)
        return rules

    def where_to_rotate(self, source):
        """
        Нам дается строка вида:

        "20 mb >> logs_dir"

        Слева от '>>' здесь правила, справа директория, куда перемещать логи при ротации.

        Так вот, данный метод возвращает правую часть.
        Если директория не была указана - возвращаем путь к стандартной директории.
        """
        if source is None:
            return self.get_standart_destination()
        splitted_source = source.split('>>')
        if len(splitted_source) == 1:
            result = None
        elif len(splitted_source) == 2:
            result = splitted_source[1]
            if result == '':
                result = None
        else:
            raise ValueError('The rotation command is incorrectly formatted.')
        if result is None:
            return self.get_standart_destination()
        result = result.strip()
        return result

    def extract_rules_string_from_source(self, source):
        """
        Нам дается строка вида:

        "20 mb >> logs_dir"

        Слева от '>>' здесь правила, справа директория, куда перемещать логи при ротации.

        Так вот, данный метод возвращает левую часть.
        """
        if source is None:
            return None
        splitted_source = source.split('>>')
        if len(splitted_source) == 1:
            result = source
        elif len(splitted_source) == 2:
            result = splitted_source[0]
            if result == '':
                return None
        else:
            raise ValueError('The rotation command is incorrectly formatted.')
        return result

    def get_standart_destination(self):
        """
        Возвращаем название директории, куда ротируются логи, если пользователь не указал свою.
        """
        return 'logs'

    def new_filename(self):
        """
        Создаем новое имя файла при ротации.
        Оно основано на текущем времени / дате.
        """
        stamp = str(datetime.datetime.now()).replace(' ', '_')
        process_id = current_process().pid

        result = f'{stamp}_{process_id}.logs'
        return result
