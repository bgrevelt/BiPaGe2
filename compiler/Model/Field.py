from .Node import Node
from .BuildMessage import BuildMessage
import math
from Model.Collection import Collection

def _standard_size(size):
    if size <= 0:
        # Yes this is a problem, but we'll accept it here so semantic analysis can catch it
        return size
    else:
        bytes_required = math.ceil(size / 8)
        bytes_nearest_type = 2 ** (math.ceil(math.log(bytes_required, 2)))
        return bytes_nearest_type * 8


class Field(Node):
    def __init__(self, name, type, offset, token):
        super().__init__(token)
        self.name = name
        self.offset = offset
        self._type = type
        self.standard_size = _standard_size(self.size_in_bits())
        # capture size and offset default to type size and offset. If this is non-standard type set_capture will be
        # called to override these values.
        self.capture_size = self.size_in_bits()
        self.capture_offset = offset
        self.scoped = False

    def set_capture(self, size, offset):
        self.capture_size = size
        self.capture_offset = offset
        self.scoped = True

    def check_semantics(self, warnings, errors):
        self._type.check_semantics(warnings, errors)

        line, column = self.location()
        if not type(self._type) is Collection and not self.scoped and not self.is_standard_size():
            errors.append(BuildMessage(line, column, f'Non standard ({self.size_in_bits()} bits) sized Field {self.name} should be in a capture scope.'))

    # return the byte aligned offset to the field
    def capture_type_offset(self):
        return self.capture_offset

    def capture_type_mask(self):
        offset_in_capture_type = self.offset - self.capture_offset

        return (2**(self.size_in_bits() + offset_in_capture_type)) - 2**offset_in_capture_type

    def return_type_size(self):
        return _standard_size(self.size_in_bits())

    def is_signed_type(self):
        return self._type.signed()

    def is_standard_size(self):
        # anything under 8 bits is non-standard
        if self.size_in_bits() < 8:
            return False
        # standard size is a power of 2
        return math.log(self.size_in_bits(), 2).is_integer()

    def size_in_bits(self):
        return self._type.size_in_bits()

    def type(self):
        return self._type