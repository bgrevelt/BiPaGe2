from typing import List
from collections import defaultdict

class ImportNode:
    def __init__(self, path:str, imports):
        self._path = path
        self._imports = imports

    def traverse(self) -> List[str]:
        imports_in_order = []
        for imp in self._imports:
            for path in imp.traverse():
                if path not in imports_in_order:
                    imports_in_order.append(path)
        imports_in_order.append(self._path)
        return imports_in_order

    def get_imports(self):
        return self._imports

    def set_imports(self, imports):
        self._imports = imports
        
    def path(self):
        return self._path

class ImportTree:
    def __init__(self):
        self._nodes_by_path = {}
        self._parents = defaultdict(list)

    def addnode(self, path:str, imports:List[str]):
        assert path not in self._nodes_by_path, "We should not add an import multiple times"
        self._nodes_by_path[path] = ImportNode(path, imports)
        for imp in imports:
            self._parents[imp].append(path)

    def imports_in_order(self) -> List[str]:
        self._cleantree()
        return self._find_root().traverse()

    def imports_for_node(self, path):
        # Todo: it's a bit ugly that we expect cleantree to be called here
        return self._nodes_by_path[path].get_imports()

    def __contains__(self, item):
        return item in self._nodes_by_path

    def _cleantree(self):
        # We build the import tree in a 2 step fashion
        # 1) Each ImportNode contains a list of imported paths as strings
        # 2) We replace each imported path string with a reference to the ImportNode for that path
        # This method performs step (2)
        for node in self._nodes_by_path.values():
            node.set_imports([self._nodes_by_path[imp] for imp in node.get_imports()])

        #self._nodes_by_path = {path : ImportNode(path, [self._nodes_by_path[imp] for imp in node.imports()]) for path, node in self._nodes_by_path.items()}

    def _find_root(self) -> ImportNode:
        root_nodes = [path for path in self._nodes_by_path.keys() if len(self._parents[path])==0]
        assert len(root_nodes) == 1, f"There should be exactly one file that is not included by other files: {root_nodes}"
        return self._nodes_by_path[root_nodes[0]]



if __name__ == '__main__':
    tree = ImportTree()

    imports = {
        'a': ['b', 'd', 'f'],
        'b': ['c', 'd', 'e'],
        'c': ['e', 'f'],
        'd': ['f','g'],
        'e': [],
        'f': ['g'],
        'g': []
    }

    for path, imported_files in imports.items():
        tree.addnode(path, imported_files)

    for imp in tree.imports_in_order():
        assert len(imports[imp]) == 0
        # Remove files
        imports = {k:[v for v in vs if v != imp] for k,vs in imports.items()}