from dataclasses import dataclass

from polog.loggers.auto.function_logger import flog
from polog.loggers.handle.handle_log import handle_log
from polog.loggers.handle.message import message
from polog import log


@dataclass
class NameEstimation:
    possibility: bool
    reason: str = None

class NameManager:
    """
    Здесь должны проверяться на допустимость все пользовательские имена.
    """
    @classmethod
    def is_possible_level_name(cls, name):
        """
        Проверяем имя на возможность использования для уровня логирования.
        Возвращается объект NameEstimation.
        """
        if not cls.is_identifier_name(name):
            return NameEstimation(
                possibility=False,
                reason="The name of level must be python identifier compatible.",
            )

        if name.startswith('_'):
            return NameEstimation(
                possibility=False,
                reason="The name of level can't start on dander symbol.",
            )

        forbidden_names = set(dir(flog)).union(set(dir(handle_log))).union(set(dir(log))).union(set(dir(message)))
        if name in forbidden_names:
            return NameEstimation(
                possibility=False,
                reason=f'The name "{name}" cannot be used for the logging level. It is already used as a service name in the logger.',
            )

        return NameEstimation(possibility=True)

    @classmethod
    def is_possible_extra_field_name(cls, name):
        """
        Проверяем имя на возможность использования для извлекаемых полей.
        Возвращается объект NameEstimation.
        """
        if not cls.is_identifier_name(name):
            return NameEstimation(
                possibility=False,
                reason="The name of field must be python identifier compatible.",
            )

        if name.startswith('_'):
            return NameEstimation(
                possibility=False,
                reason="The name of field can't start on dander symbol.",
            )

        forbidden_names = {
            'level',
            'auto',
            'time',
            'service_name',
            'success',
            'function',
            'class',
            'module',
            'message',
            'exception_type',
            'exception_message',
            'traceback',
            'input_variables',
            'local_variables',
            'result',
            'time_of_work',
        }
        if name in forbidden_names:
            return NameEstimation(
                possibility=False,
                reason=f'The name "{name}" occupied by built-in field, you can\'t use it.',
            )

        return NameEstimation(possibility=True)

    @staticmethod
    def is_identifier_name(name):
        """
        Проверка, может ли данное имя быть использовано для обозначения переменной в python.
        """
        return name.isidentifier()
