from threading import RLock
from polog.data_structures.trees.named_tree.walker import TreeWalker
from polog.data_structures.trees.named_tree.printer import TreePrinter


class NamedTree:
    """
    Экземпляры данного класса представляют из себя деревья. Каждая нода дерева - сама по себе независимое дерево.

    Каждая нода дерева имеет имя. Идентификация конкретной ноды в дереве происходит за счет композиции имен всех родительских нод + имени конкретной ноды, через некоторый разделитель (по умолчанию - ".").

    Синтаксис работы с деревом похож на синтаксис обычного словаря:

    >>> tree = NamedTree()
    >>> tree['kek'] = 'lol'
    >>> tree['kek']
    lol
    >>> tree['kek.cheburek'] = 'lol'
    >>> tree['kek.cheburek']
    lol

    Однако при итерации по дереву возвращаются значения, хранящиеся в нодах, в порядке обхода в ширину (словарь при итерации возвращает ключи, а не значения):

    >>> list(tree)
    ['lol', 'lol']

    Количество элементов дерева возвращается по числу только заполненных нод (пустые ноды не учитываются):

    >>> tree['chmek.perekek'] = 'perekekoperekek'
    >>> len(tree)
    3

    Оператор "in" работает на базе ключей. Оператор "del" также работает по ключам.

    Большинство операций с деревом потокобезопасны за счет применения локов.

    Дерево хранит пустые ноды в случае, если они ведут к хотя бы одной заполненной ноде. Иначе они автоматически удаляются. Строковое представление дерева не учитывает, пустые ноды или нет, выводятся тупо все ноды.
    """
    def __init__(self, keys_separator='.', key_checker=lambda key: key.isidentifier(), value_checker=lambda value: True, parent=None, name=None):
        self.keys_separator = keys_separator
        self.key_checker = key_checker
        self.value_checker = value_checker
        self.parent = parent
        self.name = name

        self.value = None
        self.childs = {}
        self.walker = TreeWalker(self)
        self.printer = TreePrinter(self)
        self.lock = RLock()

    def __getitem__(self, key):
        """
        Получение значения по ключу.

        Ключ - это строка, состоящая из конкатенированных через некоторый установленный разделитель имена нод. Если по данному пути существует нода дерева с хранящимся в ней значением, оно будет возвращащено. Иначе - будет поднято исключение KeyError.
        """
        item = self.get(key)
        if item is None:
            raise KeyError(f"{key}")
        return item

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
            result = 0
            for value in self.walker.bfs_values():
                result += 1
            return result

    def __iter__(self):
        with self.lock:
            return self.walker.bfs_values()

    def __contains__(self, key):
        with self.lock:
            keys = self.get_converted_keys(key)
            node = self.search_node(keys)
            if node is None:
                return False
            return True

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise KeyError('The key in the tree can only be a string.')
        with self.lock:
            keys = self.get_converted_keys(key)
            node = self.search_node(keys)
            if node is None:
                raise KeyError(f'The key "{key}" is not registered.')
            node.delete_value()
            self.cut_empty_branch(node, break_on=self)

    def __str__(self):
        with self.lock:
            return self.printer.get_indented_representation()

    @staticmethod
    def cut_empty_branch(node, break_on=None):
        while node is not None:
            parent = node.parent
            if parent is None:
                break
            childs_to_delete = []
            for child_name, child in parent.childs.items():
                if child is break_on:
                    return
                if not len(child):
                    childs_to_delete.append(child_name)
            for name in childs_to_delete:
                del parent.childs[name]
            node = parent

    def delete_value(self):
        self.value = None

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

    def get_converted_keys(self, key):
        if not isinstance(key, str):
            raise KeyError('The key in the tree can only be a string.')
        keys = key.split(self.keys_separator)
        for key in keys:
            if not self.key_checker(key):
                raise KeyError(f"You can't use \"{key}\" as the node name.")
        return keys
