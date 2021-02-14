from ..Node import Node
from ..BuildMessage import BuildMessage


class Reference(Node):
    def __init__(self, name, referenced_type, token):
        super().__init__(token)
        self._name = name
        self._referenced_type = referenced_type

    def size_in_bits(self):
        if self._referenced_type is not None:
            return self._referenced_type.size_in_bits()
        else:
            return 8

    def signed(self):
        if self._referenced_type is not None:
            return self._referenced_type.signed()
        else:
            return False

    def referenced_type(self):
        return self._referenced_type

    def check_semantics(self, warnings, errors):
        line, column = self.location()
        if self._referenced_type is None:
            errors.append(BuildMessage(line, column,
                                       f'Reference "{self._name}" cannot be resolved'))