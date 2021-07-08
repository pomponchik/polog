import weakref
from threading import Lock
from polog.core.stores.settings.settings_store import SettingsStore


class RegisteringExceptions:
    """
    Класс, хранящий в себе информацию о встреченных ранее исключениях.
    Эту информацию необходимо сохранять, чтобы не записывать информацию об одной и той же ошибке
    """

    exceptions = {}
    lock = Lock()

    def __init__(self):
        self.settings = SettingsStore()

    def decide(self, exception):
        """
        Метод, которому нужно предъявить объект исключения, и он решит - нужно его логировать или нет.

        Если нужно - вернет True, если нет - False.

        Нужность логирования определяется по 2-м параметрам:
        1. Встречалось ли уже данное исключение ранее.
        2. Состояние флага "only_unique_exceptions" в настройках.

        Логировать нужно во всех случаях, когда исключение ранее не встречалось, а также если уже встречалось, но настройка "only_unique_exceptions" стоит в положении False.

        Также, если исключение ранее не встречалось, оно будет "запомнено", чтобы его уже можно было узнать при следующей встрече. Поэтому данный метод - единственный в классе, с которым непосредственно взаимодействует пользователь.
        """
        with self.lock:
            if self.uniqueness_check(exception):
                self.add(exception)
                return True
                ...
            return False

    def add(self, exception):
        ref = weakref.ref(exception)
        exception_id = id(exception)
        self.exceptions[exception_id] = ref
        self.create_finalizer(exception, exception_id)

    def remove(self, exception_id):
        self.exceptions.pop(exception_id)

    def uniqueness_check(self, exception):
        """
        Проверка исключения на "знакомость".

        Если оно еще не встречалось, возвращаем True, иначе - False.
        """
        exception_id = id(exception)
        return not (exception_id in self.exceptions)

    def create_finalizer(self, exception, exception_id):
        def finalize():
            with self.lock:
                self.remove(exception_id)
        weakref.finalize(exception, finalize)
