from polog.handlers.abstract.base import BaseHandler
from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper
from polog.handlers.file.base_formatter import BaseFormatter


class file_writer(BaseHandler):
    def __init__(self, file, formatter=None, rotation=None, forced_flush=True, separator='\n', only_errors=False, filter=None, alt=None, file_wrapper=FileDependencyWrapper, base_formatter=BaseFormatter):
        self.file = file_wrapper(file)
        self.forced_flush = forced_flush
        self.filter = filter
        self.only_errors = only_errors
        self.alt = alt
        self.base_formatter = base_formatter(separator)
        self.formatter = self.get_formatter(formatter)

    def do(self, content):
        self.file.write(content)
        self.maybe_flush()

    def get_content(self, args, **kwargs):
        return self.formatter(args, **kwargs)

    def maybe_flush(self):
        if self.forced_flush:
            self.file.flush()

    def get_formatter(self, maybe_formatter):
        if callable(maybe_formatter):
            return maybe_formatter
        return self.base_formatter_wrapper

    def base_formatter_wrapper(self, args, **kwargs):
        result = self.base_formatter(args, **kwargs)
        return result
