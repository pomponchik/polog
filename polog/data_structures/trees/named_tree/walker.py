class TreeWalker:
    """
    Объекты этого класса инкапсулируют логику обходов по дереву.
    """
    def __init__(self, tree):
        self.tree = tree

    def bfs(self):
        """
        Функция-генератор для обхода в ширину (BFS) по дереву.

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
        Функция-генератор для обхода в ширину (BFS) по дереву.

        На каждой итерации возвращает значение, хранящееся в ноде. Пустые ноды игнорируются.
        """
        for node in self.bfs():
            if node.value is not None:
                yield node.value

    def dfs(self):
        yield from self.recursive_dfs(self.tree)

    def recursive_dfs(self, node):
        yield node
        for child in node.childs.values():
            yield from self.recursive_dfs(child)
