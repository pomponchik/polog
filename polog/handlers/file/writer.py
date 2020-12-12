from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper


class file_writer:
    def __init__(self, file, formatter=None, rotation=None, filter=None, only_errors=False, file_wrapper=FileDependencyWrapper):
        
