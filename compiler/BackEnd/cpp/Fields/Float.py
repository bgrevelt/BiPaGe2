from .Field import Field

class Float32(Field):
    def __init__(self, field, settings):
        super().__init__(field, 'float', '0.f', settings)

class Float64(Field):
    def __init__(self, field, settings):
        super().__init__(field, 'double', '0.', settings)