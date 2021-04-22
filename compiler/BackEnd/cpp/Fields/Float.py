from .Field import Field

class Float(Field):
    def __init__(self, type_name, field, endianness):
        super().__init__(type_name, field, endianness)

    def getter_body(self):
        body = f'*reinterpret_cast<const {self._cpp_type}*>(data_ + {self._dynamic_offset} {self.offset_name()})'
        body = self.add_swap_if_required(body);
        return f'return {body};'

    def builder_serialize_body(self):
        return f'*reinterpret_cast<{self._cpp_type}*>(sink + {self._dynamic_offset} {self.offset_name()}) = {self.add_swap_if_required(self._field.name+"_")};\n'

    def to_string_code(self, string_stream_var_name):
        return f'{string_stream_var_name} << {self._field.name}();'

class Float32(Float):
    def __init__(self, type_name, field, endianness):
        super().__init__(type_name, field, endianness)

    def cpp_type(self):
        return 'float'

    def default_value(self):
        return '0.f'

class Float64(Float):
    def __init__(self, type_name, field, endianness):
        super().__init__(type_name, field, endianness)

    def cpp_type(self):
        return 'double'

    def default_value(self):
        return '0.'