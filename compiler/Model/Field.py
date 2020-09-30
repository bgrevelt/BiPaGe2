from .Node import Node
from .BuildMessage import BuildMessage
import math

class Field(Node):
    def __init__(self, name, type, offset, token):
        super().__init__(token)
        self.name = name
        self.offset = offset
        self.size_in_bits = int("".join([c for c in type if c.isnumeric()]))
        self.type = "".join([c for c in type if not c.isnumeric()])

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

        if self.encapsulating_type_size() > 64:
            pass
            errors.append(BuildMessage(line, column,
                                       f'Field {self.name} cannot be captured in a type that is 64 bits or less in size. Field size is {self.size_in_bits} bits. Field offset is {self.offset} bits. Capture type would need to be {self.encapsulating_type_size()} bits.'))

    def encapsulating_type_offset(self):
        return (self.offset // 8) * 8

    def encapsulating_type_size(self):
        offset_in_byte = self.offset % 8
        return self._encapsulating_type_size(offset_in_byte + self.size_in_bits)

    def encapsulated_type_mask(self):
        offset_in_byte = self.offset % 8
        return (2**(self.size_in_bits + offset_in_byte)) - 2**offset_in_byte

    def return_type_size(self):
        return self._encapsulating_type_size(self.size_in_bits)

    def _encapsulating_type_size(self, size):
        bytes_required = math.ceil(size / 8)
        bytes_nearest_type = 2 ** (math.ceil(math.log(bytes_required, 2)))
        return bytes_nearest_type * 8

    def is_signed_type(self):
        return self.type in ['int', 'float']
