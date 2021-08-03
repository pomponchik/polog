from threading import Lock
from polog.errors import DoubleSettingError, AfterStartSettingError


class SettingPoint:
    """
    В глобальном классе настроек имени каждой отдельной настройки соответствует экземпляр данного класса.
    Вся логика, связанная с проверкой возможности сохранить новое значение для конкретной настройки, находится здесь. Таким образом, в основном классе остается только функциональность агрегации.
    """
    def __init__(self, default, change_once=False, change_only_before_start=False, prove=None, converter=None, no_check_first_time=False, action=None, conflicts=None, read_lock=False, shared_lock_with=()):
        """
        Значения параметров:

        default (любой тип данных) - исходное значение параметра. В дальнейшем его возможно изменить методом self.set().
        change_once (bool) - запрет сохранять новое значение параметра более 1 раза. False (по умолчанию) - не запрещено.
        change_only_before_start (bool) - запрет на сохранение новых значений после записи первого лога.
        prove (callable, 1 аргумент) - функция, в которую скармливается каждое новое сохраняемое значение, предназначенная для проверки его валидности. Она должна принимать один параметр, и для валидных значений возвращать True, для остальных - False. По умолчанию для дефолтного значения проверка тоже делается, но это можно отключить, см. параметр "no_check_first_time".
        converter (callable, 1 аргумент) - функция, которая применяется к каждому сохраняемому значению непосредственно перед сохранением, если она была передана в конструктор, возвращает новое значение. Используется в случаях, когда пользователь может передавать значения в некотором произвольном формате, а внутри программы используется единый формат. Важно: проверка валидности значения осуществляется до применения данной функции, т. е. к вводу в произвольном формате.
        no_check_first_time (bool) - не проверять дефолтное значение. False (по умолчанию) - проверять.
        action (callable, 3 аргумента) - действие, которое необходимо произвести сразу после присвоения нового значения. Принимает 3 аргумента: старое значение настройки, новое значение и экземпляр класса-агрегатора, чтобы была возможность обратиться к смежным полям.
        conflicts (dict, в котором каждый ключ - строка с названием другого поля настроек, а каждое значение - callable на 3 аргумента) - набор функций, каждая из которых возвращает True или False, в зависимости от того, соответственно, есть конфликт с данным полем или нет. Каждая из функций в словаре принимает 3 аргумента: старое значение настройки, новое значение и текущее значение поля, конфликт с которым проверяется.
        read_lock (bool) - блокировка на чтение (т. е. не только на запись).
        shared_lock_with (iterable со строками) - перечисление названий других полей настроек, с которыми объект блокировки должен быть общий.
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
        self.shared_lock_with = shared_lock_with
        self.lock = Lock()
        self.set_action(action)
        self.set_conflicts(conflicts)
        self.set_read_lock(read_lock)

    def __str__(self):
        return f'<SettingPoint object "{self.name}" with value {self.value}, #{id(self)}>'

    def set(self, value):
        """
        Здесь мы сохраняем новое значение настройки.

        Перед сохранением значения, прогоняем несколько проверок, и сохраняем его только если они все пройдены, иначе поднимаем одно из исключений.

        Проверка 1: запрещено ли повторно назначать менять данную настройку, и, если да, менялась ли она уже ранее?
        Проверка 2: запрещено ли менять данную настройку после записи первого лога, и, если да, был ли первый лог уже записан?
        Проверка 3: используем функцию, переданную в конструктор, для проверки валидности переданного значения. Обычно там проверяются типы данных, но могут быть и иные проверки.
        Проверка 4: есть ли у нового значения конфликты с какими-то другими полями настроек?

        Если в конструктор была передана функция-конвертер для значений, перед сохранением значение прогоняется через нее.
        Если в конструктор была передана функция-действие (action), она выполняется после присвоения нового значения.

        Нюанс, связанный с многопоточностью: стоит учитывать, что блокировка потока используется только при сохранении нового значения настройки, а не при чтении значения (если только при инициализации объекта не был установлен режим защищенного чтения). Это значит, что пока один поток назначает новое значение, проводя все проверки, другой поток по-прежнему может считать старое значение.
        """
        with self.lock:
            if self.changed and self.change_once:
                raise DoubleSettingError("You have already configured this option before. You can't change this option twice.")
            if self.change_only_before_start and self.store['started']:
                raise AfterStartSettingError('This item of settings can be changed only before the first log entry. The first record has already occurred.')
            if not self.prove_value(value):
                raise ValueError(f"You can't use the \"{value}\" object to change the settings in this case. Read the documentation.")
            if self.converter is not None:
                value = self.converter(value)
            old_value = self.value
            self.prove_conflicts(old_value, value)
            self.value = value
            self.do_action(old_value, value)
            self.changed = True

    def get(self):
        """
        Абстрактный метод получения текущего значения пункта настроек.

        При инициализации объекта он будет перезаписан одной из реальных имплементаций, в зависимости от входных аргументов.
        """
        raise NotImplementedError # pragma: no cover

    def unlocked_get(self):
        """
        Получение хранящегося значения.

        В данном методе не используется блокировка потока, возможно состояние гонки.
        """
        return self.value

    def locked_get(self):
        """
        Защищенное чтение.

        Если объект был инициализирован с аргументом read_lock == True, метод get() подменяется данным, и чтение значений пока производится их запись становится невозможным.
        Это особенно полезно, когда к пункту настроек привязано какое-то неатомарное хрупкое действие, которое нельзя проводить параллельно в двух разных местах - например, перезагрузка движка.
        """
        with self.lock:
            return self.value

    def do_action(self, old_value, new_value):
        """
        Выполняем функцию, переданную пользователем, после сохранения нового значения.
        """
        try:
            self.action(old_value, new_value, self.store)
        except Exception:
            pass

    def prove_conflicts(self, old_value, new_value):
        """
        Некоторые значения одних полей настроек могут быть несовместимы с некоторыми значениями других полей.
        Здесь мы проверяем, есть ли такие конфликты, и если они есть - поднимаем ValueError.
        """
        for field_name, conflict_checker in self.conflicts.items():
            if conflict_checker(old_value, new_value, self.store.force_get(field_name)):
                raise ValueError(f'The new value "{new_value}" of the field "{self.name}" is incompatible with the current value "{self.store[field_name]}" of the field "{field_name}".')

    def share_lock_object(self):
        """
        Передаем объект Lock другим полям настроек, перечисленным в self.shared_lock_with.

        Это может быть полезно, когда несколько полей настроек взаимосвязаны.
        """
        for name in self.shared_lock_with:
            if name == self.name:
                raise KeyError(f'You are trying to mix the block of field "{name}" with itself.')
            other_point = self.store.get_point(name)
            other_point.set_lock_object(self.get_lock_object())

    def get_lock_object(self):
        """
        Получить объект блокировки.

        Метод используется при обмене блокировками у взаимосвязанных полей.
        """
        return self.lock

    def set_lock_object(self, lock):
        """
        Задать новый объект блокировки.

        Метод используется при обмене блокировками у взаимосвязанных полей.
        """
        self.lock = lock

    def set_read_lock(self, read_lock):
        """
        Подменяем стандартный незащищенный блокировкой метод get() защищенным.

        Подмена производится, если при инициализации объекта был передан аргумент read_lock == True.
        """
        if read_lock:
            self.get = self.locked_get
        else:
            self.get = self.unlocked_get

    def set_conflicts(self, conflicts):
        """
        Сохраняем словарь с конфликтами.

        Некоторые пары значений в разных полях настроек могут конфликтовать. В словаре в качестве ключей используются названия этих полей, а в качестве значений - функции. Если функция возвращает True, значит конфликт есть и данное новое значение принимать нельзя, есл False - все хорошо, конфликта нет.

        Каждая функция для проверки конфликтов принимает 3 позиционных аргумента:
        1. Старое значение текущего пункта настроек.
        2. Новое значение текущего пункта настроек.
        3. Текущее значение того пункта настроек, конфликт с которым мы проверяем.

        Проверка конфликтов осуществляется при каждом сохранении нового значения, после всех прочих проверок (кроме присвоения дефолтного значения - там проверки на конфликты нет).
        Если конфликт обнаружен, новое значение сохранено не будет, поднимется ValueError.
        """
        self.conflicts = conflicts if conflicts is not None else {}

    def set_action(self, action):
        """
        Сохраняем функцию, которую следует применять после сохранения нового значения поля.

        В нее должны передаваться 3 аргумента: старое значение поля, новое значение поля и объект класса-агрегатора настроек.
        Данная функция обеспечивает "реактивность" настроек. При изменении настройки не просто меняется одна переменная внутри поля, но и производятся какие-то действия вовне.
        """
        self.action = action if action is not None and callable(action) else lambda old_value, new_value, store: True

    def set_store_object(self, store):
        """
        Данный метод используется для оповещения полей настроек о классе-агрегаторе.

        Это необходимо, чтобы поля могли кастомизировать свое поведение в зависимости друг от друга, получая друг к другу доступ через класс-агрегатор.
        """
        with self.lock:
            self.store = store

    def set_name(self, name):
        """
        Оповещение пункта настроек о его имени.

        Производится классом-агрегатором.
        """
        with self.lock:
            self.name = name

    def prove_value(self, value):
        """
        Проверка нового значения.

        Пользователь передает для этого собственную функцию в конструкторе. Если он не передал свою функцию, проверка не проводится и данный метод всегда возвращает True.
        """
        return self.prove is None or self.prove(value)
