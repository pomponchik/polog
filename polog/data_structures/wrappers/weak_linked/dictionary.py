import weakref
from threading import RLock
from contextlib import suppress


class LockedWeakKeyValueDictionary:
    def __init__(self):
        self.lock = RLock()
        self.data = weakref.WeakKeyDictionary()

    def __setitem__(self, key, value):
        if value is None:
            raise TypeError("The value can't be None.")
        weak_key = weakref.ref(key)
        with self.lock:
            def finalizer(rf):
                with suppress(TypeError):
                    del self[weak_key()]
            self.data[key] = weakref.ref(value, finalizer)

    def __getitem__(self, key):
        with self.lock:
            data = self.get(key)
            if data is None:
                raise KeyError(key)
            return data

    def __delitem__(self, key):
        with self.lock:
            del self.data[key]

    def __str__(self):
        with self.lock:
            local_data = ', '.join([f'{key}: ' + str(value()) if not isinstance(value(), str) else f'"{value}"' for key, value in self.data.items()])
            if not local_data:
                return f'<{type(self).__name__} object (empty)>'
            return f'<{type(self).__name__} object with data: {{{local_data}}}>'

    def __contains__(self, key):
        return key in self.data

    def __hash__(self):
        raise TypeError(f"unhashable type: '{type(self).__name__}'")

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for key in self.keys():
            yield key

    def get(self, key):
        with self.lock:
            weak_data = self.data.get(key)
            if weak_data is not None:
                return weak_data()

    def keys(self):
        return self.data.keys()

    def values(self):
        for value in self.data.values():
            value = value()
            if value is not None:
                yield value

    def items(self):
        for key in self.keys():
            value = self.get(key)
            if value is not None:
                yield key, value()

    def pop(self, key, *defaults):
        if len(defaults) > 1:
            raise TypeError(f'pop expected at most 2 arguments, got {len(defaults)}')

        default_exist = len(defaults) == 1

        with self.lock:
            item = self.get(key)
            if item is None:
                if default_exist:
                    return defaults[0]
                raise KeyError(key)
            del self[key]
            return item
