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

    Оператор "in" работает на базе ключей:

    >>> 'kek' in tree
    True

    Оператор "del" также работает по ключам:

    >>> del tree['kek']
    >>> 'kek' in tree
    False

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

        Потокобезопасно.
        """
        item = self.get(key)
        if item is None:
            raise KeyError(f"{key}")
        return item

    def __setitem__(self, key, value):
        """
        Сохранение значения по ключу.

        В качестве значения нельзя использовать None.

        Создание нод (в том числе пустых промежуточных) происходит полностью автоматически. Потокобезопасно.
        """
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
        """
        Получение размера дерева.

        Под размером подразумевается число НЕ пустых нод дерева.

        Потокобезопасно.
        """
        with self.lock:
            result = 0
            for value in self.walker.bfs_values():
                result += 1
            return result

    def __iter__(self):
        """
        Получение объекта итератора по дереву.

        Итерация происходит в порядке обхода нод в ширину, начиная с корневой ноды дерева. Итерация происходит по ЗНАЧЕНИЯМ.

        Итерация по дереву НЕ ЯВЛЯЕТСЯ потокобезопасной. Также, дерево не защищено от вставки/удаления в процессе итерации.
        """
        with self.lock:
            return self.walker.bfs_values()

    def __contains__(self, key):
        """
        Проверка, что по заданному ключу в дереве есть значение.
        """
        with self.lock:
            keys = self.get_converted_keys(key)
            node = self.search_node(keys)
            if node is None:
                return False
            return True

    def __delitem__(self, key):
        """
        Удаление значения из дерева по ключу.

        Если у ноды, из которой удаляется значение, нет потомков, она автоматически удаляется из дерева.
        Если выше ноды, из которой удаляется значение, была нода без значения, она будет также автоматически удалена. Вернее, удалена будет вся ветка, состоящая из пустых нод, до первой значащей ноды.
        Если ниже ноды, из которой удаляется значение, есть другая нода, в которой есть значение, текущая нода удалена из дерева удалена не будет. В ней будет удалено значение.

        Потокобезопасно.
        """
        if not isinstance(key, str):
            raise KeyError('The key in the tree can only be a string.')

        with self.lock:
            keys = self.get_converted_keys(key)
            node = self.search_node(keys)
            if node is None or node.value is None:
                raise KeyError(f'The key "{key}" is not registered.')
            node.delete_value()
            self.cut_empty_branch(node, break_on=self)

    def __str__(self):
        """
        Получение строковой репрезентации дерева.

        Потокобезопасно.
        """
        with self.lock:
            return self.printer.get_indented_representation()

    @staticmethod
    def cut_empty_branch(node, break_on=None):
        """
        Очистка дерева от лишних пустых нод. То есть от таких, которые не ведут к заполненным нодам.

        Алгоритм основан на проходе вверх по нодам дерева (подразумевается, что дерево у нас растет "вверх ногами", то есть корень дерева - это самая верхняя нода). Для каждой ноды при проходе мы считаем количество значений в поддереве, которое с нее начинается. Если оно равно нулю - удаляем ноду.
        Подъем останавливается, если мы достигли ноды, обозначенной как break_on. Если нода break_on не передана, подъем идет до корня. Это может приводить к неожиданным последствиям, если данный метод запускается на поддереве какого-то более крупного дерева - будут зааффекчены ноды того дерева, которые стоят выше по иерархии относительно поддерева.

        Не потокобезопасно, подразумевается вызов из защищенных локом методов.
        """
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
        """
        "Обнуление" содержимого ноды.

        Не потокобезопасно, подразумевается вызов из защищенных локом методов.
        """
        self.value = None

    def get(self, key):
        """
        Получаем значение по ключу. Примерно то же самое, что .__getitem__(), но здесь возвращается None, когда значения нет.

        Потокобезопасно.
        """
        with self.lock:
            if key == self.keys_separator:
                return self.value
            keys = self.get_converted_keys(key)
            node = self.search_node(keys)
            if node is None:
                return node
            return node.value

    def search_node(self, keys):
        """
        Поиск ноды по указанному пути в виде списка названий нод. Если нода найдена, она будет возвращена, иначе возвращается None.

        Не потокобезопасно, подразумевается вызов из защищенных локом методов.
        """
        if not keys:
            return None

        if len(keys) == 1 and keys[0] == self.keys_separator:
            return self

        node = self
        for key in keys:
            next_node = node.childs.get(key)
            if next_node is None:
                return None
            node = next_node
        return node

    def search_or_create_node(self, keys):
        """
        То же самое, что .search_node(), но в случае, если нода не найдена, она создается. Если необходимо - создаются пустые промежуточные ноды.
        Таким образом, метод всегда возвращает ноду - либо найденную в дереве, либо созданную только что.

        Не потокобезопасно, подразумевается вызов из защищенных локом методов.
        """
        if len(keys) == 1 and keys[0] == self.keys_separator:
            return self

        node = self
        for key in keys:
            next_node = node.childs.get(key)
            if next_node is None:
                next_node = node.create_child(key)
            node = next_node
        return node

    def create_child(self, name):
        """
        Для ноды, от которой вызывается данный метод, создается потомок без значения, с указанным именем.

        name - имя НОДЫ потомка, не полное имя, состоящее из пути к потомку через несколько нод.

        У одной ноды не может быть двух потомков с одинаковыми именами. При попытке продублировать потомка будет поднято исключение.

        Создание потомка происходит в 3 этапа:
        1. Проверяем, что потомка с таким же именем у ноды пока нет.
        2. Создаем элемент того же класса, как тот, от которого вызван данный метод, передавая ему в конструктор все те же переменные, что были использованы при конструировании текущей ноды.
        3. Прописываем свежесозданную ноду в словарь с потомками текущей ноды.

        Метод возвращает свежесозданную ноду.

        Потокобезопасно.
        """
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
        """
        Получаем полное имя ноды.

        Полное имя конструируется проходом вверх по дереву (т. е. по направлению к корню), путем конкатенации имен всех встреченных нод через установленный сепаратор.
        Если метод был вызван у корневой ноды, и имя у нее не прописано, по умолчанию будет возвращен сепаратор. Если был передан аргумент default - будет возвращен он.

        Поведение метода может показаться неожиданным, если он был вызван от ноды, дерева, которое было отделено от другого, более крупного дерева. Полное имя будет считаться проходом до корня исходного дерева.

        Потокобезопасно.
        """
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
        """
        Сепарируем ключ в список имен нод.

        То есть, если был подан ключ "lol.kek.cheburek" (установленный сепаратор - "."), он будет преобразован в список ["lol", "kek", "cheburek"].

        Имя каждой ноды проверяется на допустимость. Если проверка не пройдена - поднимается KeyError.

        Не потокобезопасно, подразумевается вызов из защищенных локом методов.
        """
        if not isinstance(key, str):
            raise KeyError('The key in the tree can only be a string.')

        if key == self.keys_separator:
            return [key]
        keys = key.split(self.keys_separator)
        for key in keys:
            if not self.key_checker(key):
                raise KeyError(f"You can't use \"{key}\" as the node name.")
        return keys

    def put_node(self, key, new_node):
        """
        Вставляем ноду, переданную извне, в текущее дерево.

        Если в текущем дереве уже есть нода по тому же адресу, она и все ее потомки "перетираются" новой нодой.

        Важно: необходимо всегда заменять исходное дерево тем, что было возвращено из данного метода.
        Это необходимо, поскольку, если новая нода вставляется в корень дерева, она должна перетереть корень, а это возможно сделать только извне.

        Также важно учитывать, что вставка новых нод в дерево является опасной с точки зрения образования циклов операцией.
        Необходимо следить, чтобы вставляемая нода не принадлежала тому же дереву еще до вставки. Непосредственно при вставке такая проверка не делается.

        Потокобезопасно.
        """
        if key == self.keys_separator:
            return new_node
        
        keys = self.get_converted_keys(key)

        with self.lock:
            node = self
            for index, key in enumerate(keys):
                if index == len(keys) - 1:
                    node.childs[key] = new_node
                    return self
                else:
                    next_node = node.childs.get(key)
                    if next_node is None:
                        next_node = node.create_child(key)
                    node = next_node
            return node
