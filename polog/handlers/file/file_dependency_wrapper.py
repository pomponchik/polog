import os
import sys
import shutil
import pathlib

from polog.handlers.file.locks.double_lock import DoubleLock


class FileDependencyWrapper:
    """
    Обертка для системных функций по работе с файлами.
    """

    def __init__(self, file, lock_type):
        """
        На вход подается путь к файлу, файловый объект, либо ничего.

        В первом случае нужно открыть файл.
        Во втором - удостовериться, что перед нами именно файловый объект, т. е. что он имеет соответствующий интерфейс.
        В третьем - использовать stdout.

        file - список с аргументами от пользователя. Он валиден, если пуст, либо содержит 1 элемент - файловый объект или строку с путем к файлу.
        """
        self.file, self.filename = self.get_file_object(file)
        self.lock = DoubleLock(self.filename, lock_type)

    def is_file_object(self, file):
        """
        Проверяем, что поданный объект является файловым.
        Файловым считается объект, имеющий набор методов, перечисленный в mandatory_methods.
        """
        mandatory_methods = (
            'read',
            'write',
            'close',
        )
        attributes = dir(file)
        for method_name in mandatory_methods:
            if not method_name in attributes:
                return False
            attribute = getattr(file, method_name)
            if not callable(attribute):
                return False
        return True

    def get_file_object(self, maybe_filename):
        """
        Пользователь подает на вход имя файла (вернее, путь к нему) или непосредственно файловый объект.
        Здесь нам нужно понять, что именно он подал, и вернуть в любом случае файловый объект. То есть, если он дал название файла - открыть файл и вернуть файловый объект.
        """
        if not maybe_filename:
            return sys.stdout, None
        if len(maybe_filename) > 1:
            raise ValueError('You can specify only one file name for one file handler.')
        maybe_filename = maybe_filename[0]
        if not self.is_file_object(maybe_filename):
            if not isinstance(maybe_filename, str):
                raise ValueError('A file object or string with the file name is expected.')
            file = open(maybe_filename, 'a', encoding='utf-8')
            filename = maybe_filename
        else:
            file = maybe_filename
            filename = None
        return file, filename

    def write(self, log_string):
        """
        Запись строки в файл.
        """
        with self.lock:
            self.file.write(log_string)

    def close(self):
        """
        Закрываем файл.
        """
        self.file.close()

    def open(self, filename):
        """
        Открываем файл.
        Работает только в том случае, если исходно пользователь передал имя файла, а не файловый объект.
        """
        self.file = open(filename, 'a', encoding='utf-8')

    def reopen(self):
        """
        Закрываем файл и открываем снова.
        Работает только в том случае, если исходно пользователь передал имя файла, а не файловый объект.
        """
        self.close()
        self.open(self.filename)

    def flush(self):
        """
        Сброс буфера в файл.
        """
        with self.lock:
            self.file.flush()

    def get_size(self):
        """
        Узнаем размер файла (в байтах).
        """
        if self.filename is not None:
            stat = os.stat(self.filename)
            result = stat.st_size
            return result
        return 0

    def move_file(self, path_to_copy):
        """
        Перемещаем исходный файл в path_to_copy.

        Перемещение файла - опасный процесс с точки зрения concurrency. Если его не защитить блокировками, возможна ситуация, когда, к примеру, один актор начал перемещать файл, уже скопировал его значение в новый, но старый еще не удалил, и в это время другой актор что-то записал в файл, после чего первый его удалил.
        Для наших целей для обеспечения целостности записей требуется аж 2 вида блокировок:
        1. Блокировка файла на уровне ОС. Делается, чтобы другие процессы / потоки, открывшие параллельно тот же файл, не могли тут ничего сломать, пока мы работаем с файлом.
        2. Блокировка на уровне потока. Нужна, поскольку с одним обработчиком (читай - одним и тем же файловым объектом) могут параллельно работать воркеры из нескольких потоков.
        """
        with self.lock:
            try:
                shutil.move(self.filename, path_to_copy)
            except FileNotFoundError:
                self.make_dirs_for_path(path_to_copy)
                shutil.move(self.filename, path_to_copy)
            self.reopen()

    def make_dirs_for_path(self, path):
        """
        Для указанного пути данный метод создает все промежуточные директории, которые еще не были созданы.
        Используется, к примеру, при ротации логов, когда директория для перекладывания туда файлов еще не создана.
        """
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

    def file_exist(self, filename):
        """
        Проверяем, что файл с указанным именем существует в файловой системе.

        ВАЖНО: на результат выполнения этой функции нельзя полагаться с уверенностью. Между выполнением данного метода и моментом, когда мы начнем пытаться писать в файл / читать из него, все может измениться.
        """
        return os.path.exists(filename) and os.path.isfile(filename)
