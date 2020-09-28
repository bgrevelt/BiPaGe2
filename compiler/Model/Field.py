from .Node import Node
from .BuildMessage import BuildMessage
import math

class Field(Node):
    def __init__(self, name, type, offset, token):
        super().__init__(token)
        self.name = name
        self.type = type
        self.offset = offset
        # At this time only float|int|uint 8|16|32|64 are supported. So the size (in bits) is always at the end
        self._bits = int("".join([c for c in self.type if c.isnumeric()]))

    def size(self):
        return self._bits

    def check_semantics(self, warnings, errors):
        if self.type.startswith('float') and self._bits not in (32,64):
            errors.append(BuildMessage(self._token.line, self._token.column,
                                          f"Width {self._bits} not supported for float type. Only 32 and 64 bit float types are supported"))

    def encapsulating_type_offset(self):
        return (self.offset // 8) * 8

    def encapsulating_type_size(self):
        offset_in_byte = self.offset % 8
        bytes_required = math.ceil((offset_in_byte + self.size()) / 8)
        bytes_nearest_type = math.ceil(math.log(bytes_required, 2))
        return bytes_required * 8

    def encapsulated_type_mask(self):
        offset_in_byte = self.offset % 8
        return (2**(self.size() + offset_in_byte)) - 2**offset_in_byte
