from .Field import Field

class Float32(Field):
    def __init__(self, type_name, field, endianness):
        super().__init__(type_name, field, endianness)

    def cpp_type(self):
        return 'float'

    def default_value(self):
        return '0.'

class Float64(Field):
    def __init__(self, type_name, field, endianness):
        super().__init__(type_name, field, endianness)

    def cpp_type(self):
        return 'double'

    def default_value(self):
        return '0.'