from Model.Node import Node
from Model.BuildMessage import BuildMessage


class Collection(Node):
    def __init__(self, type, size, token):
        self._type = type
        self._size = size
        super().__init__(token)

    def size_in_bits(self):
        return self._type.size_in_bits() * self._size

    def check_semantics(self, warnings, errors):
        # TODO:
        # size not negative
        # Only stanadard types supported
        pass # Nothing to check. Just a bit