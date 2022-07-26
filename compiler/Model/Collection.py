from compiler.Model.Node import Node
from compiler.Model.BuildMessage import BuildMessage
from compiler.Model.expressions import NumberLiteral, FieldReference, DataTypeReference
from compiler.Model.types import SignedInteger, UnsignedInteger

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

    def check_semantics(self, messages):
        initial_error_count = messages.error_count()

        if self._type.check_semantics(messages) or self._size.check_semantics(messages):
            return True

        if self._type.size_in_bits() not in [8,16,32,64] and type(self._type) not in [DataTypeReference]:
            self.add_error(f'Non-standard ({self._type.size_in_bits()}) sized types not supported in collection',messages)

        # Size expression should resolve to integer
        if self._size.return_type() not in [SignedInteger, UnsignedInteger] :
            self.add_error(
                f'Only integer fields can be used to size a collection. Not {self._size.return_type().__name__}.',messages)

        evaluated = self._size.evaluate()

        if type(evaluated) is NumberLiteral:
            self.check_semantics_number_literal(messages)
        elif type(self._size) is FieldReference:
            self.check_semantics_reference(messages)
        elif self._size.return_type() is SignedInteger:
            self.add_warning('Expression sizing collection resolves to signed type. This could lead to runtime trouble if the actual value is negative.',messages)

        return messages.error_count() > initial_error_count

    def check_semantics_number_literal(self, messages):
        evaluated = self._size.evaluate()
        assert type(evaluated) is NumberLiteral
        size = evaluated.value()

        if size % 1 != 0: # floating point literal this can happen when we have a division operator that takes two literals (e.g. 3/2)
            self.add_error(f'Invalid collection size: {size}', messages)
        elif size == 0:
            self.add_warning('Collection with zero elements. This line will have no effect on the generated code.', messages)
        elif size < 0:
            self.add_error('Negative number of elements in collection.', messages)

    def check_semantics_reference(self, messages):
        assert type(self._size) is FieldReference
        if type(self._size.referenced_type().type()) is SignedInteger:
            self.add_warning(f'Collection sized by signed integer. If the field has a negative value this will lead to runtime errors.', messages)

