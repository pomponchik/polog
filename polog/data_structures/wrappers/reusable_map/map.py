class ReusableMap:
    """
    Переиспользуемый аналог встроенного map.

    Слово "переиспользуемый" означает, что по нему можно итерироваться произвольное число раз.
    Однако эта гарантия дается только при условии, что оборачиваемый итерабельный объект тоже является переиспользуемым.
    К примеру, список переиспользуемым является, поскольку по нему можно итерироваться много раз. А генератор - нет, поскольку с ним это можно сделать только 1 раз.

    По сути данный класс является оберткой вокруг map. В map все переданные при инициализации ReusableMap аргументы передаются при старте итерации, лениво. Таким образом, если вы создаете объект ReusableMap с неправильными аргументами при инициализации, вы не узнаете об этом, пока не начнете итерироваться по нему.
    """
    def __init__(self, *args, **kwargs):
        """
        Здесь сохраняются все аргументы, чтобы затем быть переданными в map.

        Важно: они никак не валидируются на данном этапе! Если вы используете ReusableMap неправильно, вы узнаете об этом только когда начнете итерироваться по объекту ReusableMap.
        """
        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        """
        Итерация по обернутому map.
        """
        return iter(map(*self.args, **self.kwargs))

    def __repr__(self):
        """
        Текстовая репрезентация.
        """
        arguments = ', '.join([str(x) for x in self.args] + [f'{key}={value}' if not isinstance(value, str) else f'{key}="{value}"' for key, value in self.kwargs])
        return f'{type(self).__name__}({arguments})'