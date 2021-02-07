from .Node import Node
from .BuildMessage import BuildMessage
from typing import List, Set, Dict, Tuple, Optional

class Enumeration(Node):
    def __init__(self, name:str, base_type, enumerands:List[Tuple[str,int]], token):
        super().__init__(token)
        self._name = name
        self._enumerands = enumerands
        self._base_type = base_type

    def name(self):
        return self._name

    def size_in_bits(self):
        return self._base_type.size_in_bits()

    def signed(self):
        return self._base_type.signed()

    def check_semantics(self, warnings, errors):
        if not self._base_type:
            line, column = self.location()
            errors.append(BuildMessage(line, column, f'Reference {self._name} cannot be resolved'))