import os
import shutil


class FileDependencyWrapper:
    """
    Обертка для системных функций по работе с файлами.
    """

    def __init__(self, file):
        """
        На вход подается путь к файлу, либо файловый объект.
        В первом случае нужно открыть файл, во втором - удостовериться, что перед нами именно файловый объект, т. е. что он имеет соответствующий интерфейс.
        """
        self.file, self.filename = self.get_file_object(file)

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
        for method_name in mandatory_methods:
            attributes = dir(file)
            if not (method_name in attributes and callable(attributes[method_name])):
                return False
        return True

    def get_file_object(self, maybe_filename):
        """
        Пользователь подает на вход имя файла (вернее, путь к нему) или непосредственно файловый объект.
        Здесь нам нужно понять, что именно он подал, и вернуть в любом случае файловый объект. То есть, если он дал название файла - открыть файл и вернуть файловый объект.
        """
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
        self.file.write(log_string)

    def flush(self):
        """
        Сброс буфера в файл.
        """
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
        """
        if self.filename is None:
            raise ValueError('Copying is not possible, the name of the source file is unknown.')
        shutil.move(self.filename, path_to_copy)

    def file_exist(self, filename):
        """
        Проверяем, что файл с указанным именем существует в файловой системе.

        ВАЖНО: на результат выполнения этой функции нельзя полагаться с уверенностью. Между выполнением данного метода и моментом, когда мы начнем пытаться писать в файл / читать из него, все может измениться.
        """
        return os.path.exists(filename) and os.path.isfile(filename)
