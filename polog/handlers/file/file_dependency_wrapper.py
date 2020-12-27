import os
import shutil


class FileDependencyWrapper:
    def __init__(self, file):
        self.file, self.filename = self.get_file_object(file)

    def is_file_object(self, file):
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
        self.file.write(log_string)

    def flush(self):
        self.file.flush()

    def get_size(self):
        if self.filename is not None:
            stat = os.stat(self.filename)
            result = stat.st_size
            return result
        return 0

    def move_file(self, path_to_copy):
        if self.filename is None:
            raise ValueError('Copying is not possible, the name of the source file is unknown.')
        shutil.move(self.filename, path_to_copy)

    def file_exist(self, filename):
        return os.path.exists(filename) and os.path.isfile(filename)
