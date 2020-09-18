from polog.logs import select, logs, db_session
from polog.base_settings import BaseSettings


class Sample:
    @staticmethod
    def for_function(function, sample=None):
        if not callable(function):
            raise ValueError(f'{function} is not function!')
        function_name = function.__name__
        function_module = function.__module__
        service_name = BaseSettings().service_name
        with db_session:
            if not (sample is None):
                logs = sample
            new_sample = select(x for x in logs if x.function == function_name and x.module == function_module and x.service == service_name)
            return new_sample
