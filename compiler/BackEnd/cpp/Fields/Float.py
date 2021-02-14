from .Field import Field

class Float32(Field):
    def __init__(self, type_name, field, endianness):
        super().__init__(type_name, field, 'float', '0.f', endianness)

class Float64(Field):
    def __init__(self, type_name, field, endianness):
        super().__init__(type_name, field, 'double', '0.', endianness)