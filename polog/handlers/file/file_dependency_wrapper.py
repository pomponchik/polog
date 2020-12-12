


class FileDependencyWrapper:
    def __init__(self, file):
        if not self.is_file_object(file):
            file = get_file_object(file)
        self.file = file

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
        if not isinstance(maybe_filename, str):
            raise ValueError('A file object or string with the file name is expected.')
        file = open(maybe_filename, 'a', encoding='utf-8')
        return file

    def write(self, log_string):
        self.file.write(log_string)

    def get_size(self):
