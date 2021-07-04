from Model.Node import Node
from Model.BuildMessage import BuildMessage
from Model.Expressions.NumberLiteral import NumberLiteral
from Model.Types.Reference import Reference
from Model.Types.SignedInteger import SignedInteger
from Model.Types.UnsignedInteger import UnsignedInteger

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
        if self._type.size_in_bits() not in [8,16,32,64]:
            self.add_message(f'Non-standard ({self._type.size_in_bits()}) sized types not supported in collection', errors)

        initial_error_count = len(errors)
        self._size.check_semantics(warnings, errors)
        if initial_error_count < len(errors):
            return

        # Size expression should resolve to integer
        if self._size.return_type() not in [SignedInteger, UnsignedInteger] :
            self.add_message(
                f'Only integer fields can be used to size a collection. Not {self._size.return_type().__name__}.',
                errors)

        evaluated = self._size.evaluate()

        if type(evaluated) is NumberLiteral:
            self.check_semantics_number_literal(warnings, errors)
        elif type(self._size) is Reference:
            self.check_semantics_reference(warnings, errors)
        elif self._size.return_type() is SignedInteger:
            self.add_message('Expression sizing collection resolves to signed type. This could lead to runtime trouble if the actual value is negative.', warnings)

    def check_semantics_number_literal(self, warnings, errors):
        evaluated = self._size.evaluate()
        assert type(evaluated) is NumberLiteral
        size = evaluated.value()

        if size % 1 != 0: # floating point literal this can happen when we have a division operator that takes two literals (e.g. 3/2)
            self.add_message(f'Invalid collection size: {size}', errors)
        elif size == 0:
            self.add_message('Collection with zero elements. This line will have no effect on the generated code.', warnings)
        elif size < 0:
            self.add_message('Negative number of elements in collection.',errors)

    def check_semantics_reference(self, warnings, errors):
        assert type(self._size) is Reference
        line, column = self.location()
        # TODO ugly import to prevent cicular import between Field and Collection
        from Model.Field import Field
        if type(self._size.referenced_type()) is Field:
            if type(self._size.referenced_type().type()) is SignedInteger:
                warnings.append(BuildMessage(line, column,
                                             f'Collection sized by signed integer. If the field has a negative value this will lead to runtime errors.'))

