from polog.data_structures.trees.named_tree.tree import NamedTree


class TreeProjector:
    """
    Объект данного класса порождает новые деревья на базе других деревьев. Как бы "проецирует" их.

    Проекция осуществляется не дерева целиком, а отдельных его "веток".

    Важно: операции вставки в получившееся по итогу дерево могут аффектить также и исходное дерево. Ноды не копируются, а перемещаются из дерева в дерево.
    """
    def __init__(self, other_tree):
        if not isinstance(other_tree, NamedTree):
            raise ValueError('An instance of the NamedTree was expected to be passed as an argument.')
        self.tree = other_tree

    def on(self, paths, not_to_root=True):
        """
        Генерируем новое дерево с копированием избранных веток из старого.

        paths - список путей к нодам из старого дерева (self.tree), которые должны быть скопированы в новое.
        not_to_root (bool) - флаг, означающий, что нельзя подменять дерево целиком.
        """
        new_tree = NamedTree()

        for path in paths:
            if path == self.tree.keys_separator and not_to_root:
                raise ValueError('Dangerous intersection of different versions of trees. This happens when trying to insert a node into the root of the tree.')
            node_to_put = self.tree.search_or_create_node(self.tree.get_converted_keys(path))
            new_tree = new_tree.put_node(path, node_to_put)

        return new_tree
