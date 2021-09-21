from threading import RLock


class NamedTree:
    """
    Экземпляры данного класса представляют из себя деревья.

    Каждая нода дерева имеет имя. Идентификация конкретной ноды в дереве происходит за счет композиции имен всех родительских нод + имени конкретной ноды, через некоторый разделитель (по умолчанию - ".").

    Синтаксис работы с деревом похож на синтаксис обычного словаря:

    >>> tree = NamedTree()
    >>> tree['kek'] = 'lol'
    >>> tree['kek']
    lol
    >>> tree['kek.cheburek'] = 'lol'
    >>> tree['kek.cheburek']
    lol

    Большинство операций с деревом потокобезопасны за счет применения локов.
    """
    def __init__(self, keys_separator='.', key_checker=lambda key: key.isidentifier(), value_checker=lambda value: True, parent=None, name=None):
        self.keys_separator = keys_separator
        self.key_checker = key_checker
        self.value_checker = value_checker
        self.parent = parent
        self.name = name

        self.value = None
        self.childs = {}
        self.lock = RLock()

    def __getitem__(self, key):
        item = self.get(key)
        if item is None:
            raise KeyError(f"'{key}'")
        return item

    def get(self, key):
        with self.lock:
            if key == self.keys_separator:
                return self.value
            keys = self.get_converted_keys(key)
            node = self.search_node(keys)
            if node is None:
                return node
            return node.value

    def search_node(self, keys):
        if not keys:
            return None
        node = self
        for key in keys:
            next_node = node.childs.get(key)
            if next_node is None:
                return None
            node = next_node
        return node

    def search_or_create_node(self, keys):
        node = self
        for key in keys:
            next_node = node.childs.get(key)
            if next_node is None:
                next_node = node.create_child(key)
            node = next_node
        return node

    def create_child(self, name):
        if not isinstance(name, str):
            raise KeyError('The key in the tree can only be a string.')
        with self.lock:
            if name in self.childs:
                raise ValueError(f'Node {self.get_full_name(default="<current>")} already has a child with name "{name}". You can\'t create another child with the same name without killing the old one.')
            child_type = type(self)
            child = child_type(keys_separator=self.keys_separator, key_checker=self.key_checker, value_checker=self.value_checker, parent=self, name=name)
            self.childs[name] = child
            return child

    def get_full_name(self, default=None):
        node = self
        result = []
        with self.lock:
            while node is not None and node.name is not None:
                result.append(node.name)
                node = node.parent
            if not result:
                if default is None:
                    return self.keys_separator
                return default
            result.reverse()
            return self.keys_separator.join(result)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise KeyError('The key in the tree can only be a string.')
        if value is None:
            raise ValueError("You can't save None in the tree.")
        if not self.value_checker(value):
            raise ValueError(f'The value of "{value}" did not pass verification.')
        with self.lock:
            keys = self.get_converted_keys(key)
            node = self.search_or_create_node(keys)
            node.value = value


    def __len__(self):
        with self.lock:
            pass

    def __iter__(self):
        with self.lock:
            pass

    def __contains__(self, key):
        with self.lock:
            keys = self.get_converted_keys(key)
            node = search_node(keys)
            if node is None:
                return False
            return True

    def __delitem__(self, key):
        with self.lock:
            keys = self.get_converted_keys(key)

    def __str__(self):
        pass

    def get_converted_keys(self, key):
        if not isinstance(key, str):
            raise KeyError('The key in the tree can only be a string.')
        keys = key.split(self.keys_separator)
        for key in keys:
            if not self.key_checker(key):
                raise KeyError(f"You can't use \"{key}\" as the node name.")
        return keys
