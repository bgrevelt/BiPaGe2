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
    def __init__(self, name, type, static_offset, dynamic_offset, token):
        super().__init__(token)
        self.name = name
        self._type = type
        self.standard_size = _standard_size(self.size_in_bits()) if self.size_in_bits() is not None else None
        # capture size and offset default to type size and offset. If this is non-standard type set_capture will be
        # called to override these values.
        self.capture_size = self.size_in_bits()
        self._static_capture_offset = static_offset
        self._dynamic_capture_offset = dynamic_offset
        self.offset_in_capture = 0
        self._scoped = False

    def set_capture(self, capture_size, static_capture_offset, dynamic_capture_offset):
        # default capture offset is the field offset
        field_offset = self._static_capture_offset

        assert field_offset >= static_capture_offset
        self.offset_in_capture =  field_offset - static_capture_offset
        self.capture_size = capture_size
        self._static_capture_offset = static_capture_offset
        self._dynamic_capture_offset = dynamic_capture_offset

        self._scoped = True

    def scoped(self):
        return self._scoped

    def offset(self):
        return self._static_capture_offset + self.offset_in_capture

    def static_capture_offset(self):
        return self._static_capture_offset

    def dynamic_capture_offset(self):
        return self._dynamic_capture_offset

    def check_semantics(self, warnings, errors):
        self._type.check_semantics(warnings, errors)

        line, column = self.location()
        if not type(self._type) is Collection and not self.scoped() and not self.is_standard_size():
            errors.append(BuildMessage(line, column, f'Non standard ({self.size_in_bits()} bits) sized Field {self.name} should be in a capture scope.'))

    def capture_type_mask(self):
        offset_in_capture_type = 0 if self.offset_in_capture is None else self.offset_in_capture

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