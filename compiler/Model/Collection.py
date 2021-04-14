from Model.Node import Node
from Model.BuildMessage import BuildMessage
from Model.Expressions.NumberLiteral import NumberLiteral
from Model.Types.Reference import Reference

class Collection(Node):
    def __init__(self, type, size, token):
        self._type = type
        self._size = size
        super().__init__(token)

    def size_in_bits(self):
        if self._size.evaluate() is None:
            return None
        else:
            return self._type.size_in_bits() * self._size.evaluate()

    def collection_size(self):
        return self._size

    def type(self):
        return self._type

    def check_semantics(self, warnings, errors):
        if type(self._size) is NumberLiteral:
            self.check_semantics_number_literal(warnings, errors)
        elif type(self._size) is Reference:
            pass #TODO
        else:
            assert False, "Unsupported size type"

    def check_semantics_number_literal(self, warnings, errors):
        assert type(self._size) is NumberLiteral
        size = self._size.evaluate()
        line, column = self.location()
        if size == 0:
            warnings.append(BuildMessage(line, column,
                                       'Collection with zero elements. This line will have no effect on the generated code.'))
        elif self._size.evaluate() < 0:
            errors.append(BuildMessage(line, column,
                                       'Negative number of elements in collection.'))
        if self._type.size_in_bits() not in [8,16,32,64]:
            errors.append(BuildMessage(line, column,
                                       f'Non-standard ({self._type.size_in_bits()}) sized types not supported in collection'))
