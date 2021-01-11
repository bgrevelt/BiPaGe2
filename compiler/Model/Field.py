from .Node import Node
from .BuildMessage import BuildMessage
import math

def _standard_size(size):
    bytes_required = math.ceil(size / 8)
    bytes_nearest_type = 2 ** (math.ceil(math.log(bytes_required, 2)))
    return bytes_nearest_type * 8


class Field(Node):
    def __init__(self, name, type, offset, token):
        super().__init__(token)
        self.name = name
        self.offset = offset
        self.type = "".join([c for c in type if not c.isnumeric()])
        self.size_in_bits = int("".join([c for c in type if c.isnumeric()]))
        self.standard_size = _standard_size(self.size_in_bits)
        # capture size and offset default to type size and offset. If this is non-standard type set_capture will be
        # called to override these values.
        self.capture_size = self.size_in_bits
        self.capture_offset = offset
        self.scoped = False

    def set_capture(self, size, offset):
        self.capture_size = size
        self.capture_offset = offset
        self.scoped = True


    def check_semantics(self, warnings, errors):
        line, column = self.location()
        if self.type == 'float' and self.size_in_bits not in (32, 64):
            errors.append(BuildMessage(line, column,
                                       f"Width {self.size_in_bits} not supported for float type. Only 32 and 64 bit float types are supported"))

        if self.type == 'int' or self.type == 'uint':
            if self.size_in_bits < 2 or self.size_in_bits > 64:
                errors.append(BuildMessage(line, column,
                                           f'Size ({self.size_in_bits}) for type {self.type} outside supported range [2-64]'))

        if self.type == 'float' and self.offset % 8 != 0:
            errors.append(BuildMessage(line, column,
                                       f'Float field {self.name} should be at a byte boundary. Current offset is {self.size_in_bits} bits.'))

        if self.type == 'int' or self.type == 'uint':
            if self.size_in_bits % 8 == 0 and self.offset % 8 != 0:
                warnings.append(BuildMessage(line, column, f'Field {self.name} is not at a byte boundary ({self.offset} bits) are you sure this is intentional?' ))

        if self.capture_size > 64:
            errors.append(BuildMessage(line, column,
                                       f'Field {self.name} cannot be captured in a type that is 64 bits or less in size. Field size is {self.size_in_bits} bits. Field offset is {self.offset} bits. Capture type would need to be {self.capture_size} bits.'))

    # return the byte aligned offset to the field
    def capture_type_offset(self):
        return self.capture_offset

    def capture_type_mask(self):
        offset_in_capture_type = self.offset - self.capture_offset

        return (2**(self.size_in_bits + offset_in_capture_type)) - 2**offset_in_capture_type

    def return_type_size(self):
        return _standard_size(self.size_in_bits)

    def is_signed_type(self):
        return self.type in ['int', 'float']

    def is_standard_size(self):
        # anything under 8 bits is non-standard
        if self.size_in_bits < 8:
            return False
        # standard size is a power of 2
        return math.log(self.size_in_bits, 2).is_integer()
