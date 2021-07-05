from threading import Lock
from polog.errors import DoubleSettingError, AfterStartSettingError


class SettingPoint:
    """
    В глобальном классе настроек имени каждой отдельной настройки соответствует экземпляр данного класса.
    Вся логика, связанная с проверкой возможности сохранить новое значение для конкретной настройки, находится здесь. Таким образом, в основном классе остается только функциональность агрегации.
    """
    def __init__(self, default, change_once=False, change_only_before_start=False, prove=None, converter=None, no_check_first_time=False):
        """
        Значения параметров:

        default (любой тип данных)- исходное значение параметра. В дальнейшем его возможно изменить методом self.set().
        change_once (bool) - запрет сохранять новое значение параметра более 1 раза. False (по умолчанию) - не запрещено.
        change_only_before_start (bool) - запрет на сохранение новых значений после записи первого лога.
        prove (callable) - функция, в которую скармливается каждое новое сохраняемое значение, предназначенная для проверки его валидности. Она должна принимать один параметр, и для валидных значений возвращать True, для остальных - False. По умолчанию для дефолтного значения проверка тоже делается, но это можно отключить, см. параметр "no_check_first_time".
        converter (callable) - функция, которая применяется к каждому сохраняемому значению непосредственно перед сохранением, если она была передана в конструктор, возвращает новое значение. Используется в случаях, когда пользователь может передавать значения в некотором произвольном формате, а внутри программы используется единый формат. Важно: проверка валидности значения осуществляется до применения данной функции, т. е. к вводу в произвольном формате.
        no_check_first_time (bool) - не проверять дефолтное значение. False (по умолчанию) - проверять.
        """
        self.prove = prove
        if not no_check_first_time and not self.prove_value(default):
            raise ValueError('The default value did not pass the standard check.')
        self.value = default
        self.converter = converter
        self.change_once = change_once
        self.no_check_first_time = no_check_first_time
        self.change_only_before_start = change_only_before_start
        self.changed = False
        self.lock = Lock()

    def set(self, value):
        """
        Здесь мы сохраняем новое значение настройки.

        Перед сохранением значения, прогоняем несколько проверок, и сохраняем его только если они все пройдены, иначе поднимаем одно из исключений.

        Проверка 1: запрещено ли повторно назначать менять данную настройку, и, если да, менялась ли она уже ранее?
        Проверка 2: запрещено ли менять данную настройку после записи первого лога, и, если да, был ли первый лог уже записан?
        Проверка 3: используем функцию, переданную в конструктор, для проверки валидности переданного значения. Обычно там проверяются типы данных, но могут быть и иные проверки.

        Если в конструктор была передана функция-конвертер для значений, перед сохранением значение прогоняется через нее.

        Нюанс, связанный с многопоточностью: стоит учитывать, что блокировка потока используется только при сохранении нового значения настройки, а не при чтении значения. Это значит, что пока один поток назначает новое значение, проводя все проверки, другой поток по-прежнему может считать старое значение.
        """
        with self.lock:
            if self.changed and self.change_once:
                raise DoubleSettingError("You have already configured this option before. You can't change this option twice.")
            if self.change_only_before_start and self.store['started']:
                raise AfterStartSettingError('This item of settings can be changed only before the first log entry. The first record has already occurred.')
            if not self.prove_value(value):
                raise ValueError(f"You can't use the \"{value}\" object to change the settings in this case. Read the documentation.")
            if self.converter is not None:
                self.value = self.converter(self.value)
            self.value = value
            # lock нужен вот поэтому.
            self.changed = True

    def get(self):
        """
        Получение хранящегося значения.
        В данном методе не используется блокировка потока, возможно состояние гонки.
        """
        return self.value

    def set_store_object(self, store):
        """
        Данный метод используется для оповещения полей настроек о классе-агрегаторе.
        Это необходимо, чтобы поля могли кастомизировать свое поведение в зависимости друг от друга, получая друг к другу доступ через класс-агрегатор.
        """
        with self.lock:
            self.store = store

    def prove_value(self, value):
        """
        Проверка нового значения. Пользователь передает для этого собственную функцию в конструкторе. Если он не передал свою функцию, проверка не проводится и данный метод всегда возвращает True.
        """
        return self.prove is None or self.prove(value)
