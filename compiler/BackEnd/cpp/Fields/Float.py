from .Field import Field

class Float32(Field):
    def __init__(self, field):
        super().__init__(field, 'float', '0.f')

class Float64(Field):
    def __init__(self, field):
        super().__init__(field, 'double', '0.')