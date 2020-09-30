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
        if self.type == 'float' and self.size_in_bits not in (32, 64):
            errors.append(BuildMessage(self._token.line, self._token.column,
                                       f"Width {self.size_in_bits} not supported for float type. Only 32 and 64 bit float types are supported"))

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
