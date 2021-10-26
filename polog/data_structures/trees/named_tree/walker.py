class TreeWalker:
    """
    Объекты этого класса инкапсулируют логику обходов по дереву.
    """
    def __init__(self, tree):
        self.tree = tree

    def bfs(self):
        """
        Функция-генератор для обхода дерева в ширину (BFS).

        На каждой итерации возвращает ноду. Ноды не проверяются на пустоту, возвращаются "как есть".
        """
        layer = [self.tree]
        while layer:
            next_layer = []
            for node in layer:
                yield node
                for child in node.childs.values():
                    next_layer.append(child)
            layer = next_layer

    def bfs_values(self):
        """
        Функция-генератор для обхода дерева в ширину (BFS).

        На каждой итерации возвращает значение, хранящееся в ноде. Пустые ноды игнорируются.
        """
        for node in self.bfs():
            if node.value is not None:
                yield node.value

    def dfs(self):
        """
        Функция-генератор для обхода дерева в глубину (DFS).

        На каждой итерации возвращает ноду. Ноды не проверяются на пустоту, возвращаются "как есть".
        """
        yield from self._recursive_dfs(self.tree)

    def _recursive_dfs(self, node):
        """
        Вспомогательный метод для реализации обхода в глубину.

        Поскольку обход реализован через рекурсию, его глубина ограничена и при ее превышении поднимется RecursionError.
        """
        yield node
        for child in node.childs.values():
            yield from self._recursive_dfs(child)
