from Model.Node import Node
from Model.BuildMessage import BuildMessage
from Model.Expressions.NumberLiteral import NumberLiteral
from Model.Types.Reference import Reference
from Model.Types.Integer import Integer

class Collection(Node):
    def __init__(self, type, size, token):
        self._type = type
        self._size = size
        super().__init__(token)

    def size_in_bits(self):
        size = self._size.evaluate()
        if type(size) is NumberLiteral:
            return self.element_size_in_bits() * size.value()
        else:
            return None

    def element_size_in_bits(self):
        return self.type().size_in_bits()

    def collection_size(self):
        return self._size

    def type(self):
        return self._type

    def check_semantics(self, warnings, errors):
        initial_error_count = len(errors)
        self._size.check_semantics(warnings, errors)
        if initial_error_count < len(errors):
            return

        # Size expression should resolve to integer
        if self._size.return_type() is not Integer:
            self.add_message(
                f'Only integer fields can be used to size a collection. Not {self._size.return_type().__name__}.',
                errors)

        evaluated = self._size.evaluate()

        if type(evaluated) is NumberLiteral:
            self.check_semantics_number_literal(warnings, errors)
        elif type(self._size) is Reference:
            self.check_semantics_reference(warnings, errors)

    def check_semantics_number_literal(self, warnings, errors):
        evaluated = self._size.evaluate()
        assert type(evaluated) is NumberLiteral
        size = evaluated.value()
        line, column = self.location()
        if size == 0:
            warnings.append(BuildMessage(line, column,
                                       'Collection with zero elements. This line will have no effect on the generated code.'))
        elif size < 0:
            errors.append(BuildMessage(line, column,
                                       'Negative number of elements in collection.'))
        if self._type.size_in_bits() not in [8,16,32,64]:
            errors.append(BuildMessage(line, column,
                                       f'Non-standard ({self._type.size_in_bits()}) sized types not supported in collection'))

    def check_semantics_reference(self, warnings, errors):
        assert type(self._size) is Reference
        line, column = self.location()
        # TODO ugly import to prevent cicular import between Field and Collection
        from Model.Field import Field
        if type(self._size.referenced_type()) is Field:
            if type(self._size.referenced_type().type()) is Integer and self._size.referenced_type().type().signed():
                warnings.append(BuildMessage(line, column,
                                             f'Collection sized by signed integer. If the field has a negative value this will lead to runtime errors.'))

