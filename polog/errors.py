class IncorrectUseOfTheDecoratorError(ValueError):
    """
    Когда в декоратор передали что-то не то.
    """
    pass

class DoubleSettingError(ValueError):
    """
    Некоторые поля настроек пользователю может быть запрещено изменять дважды.
    Если он это делает, поднимается данное исключение.
    """
    pass

class AfterStartSettingError(ValueError):
    """
    Поднимается при попытке изменить настройку, которую запрещено изменять после записи первого лога.
    """
    pass

class RewritingLogError(RuntimeError):
    """
    Поднимается при попытке одного из обработчиков отредактировать запись лога.
    """
    pass

class HandlerNotFoundError(ValueError):
    """
    Поднимается при попытке получить обработчик по ключу, который ранее не был зарегистрирован.
    """
    pass
