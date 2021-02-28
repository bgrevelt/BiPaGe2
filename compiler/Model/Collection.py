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
        line, column = self.location()
        if self._size == 0:
            warnings.append(BuildMessage(line, column,
                                       'Collection with zero elements. This is line will have no effect on the generated code.'))
        elif self._size < 0:
            errors.append(BuildMessage(line, column,
                                       'Negative number of elements in collection.'))


        if self._type.size_in_bits() not in [8,16,32,64]:
            errors.append(BuildMessage(line, column,
                                       f'Non-standard ({self._type.size_in_bits()}) sized types not supported in collection'))

    def type(self):
        return self._type