from BackEnd.cpp.Fields.Integral import Integral
from compiler.Model.Field import Field as ModelField

class Flag(Integral):
    def __init__(self, type_name:str, field:ModelField, endianness:str, settings):
        super().__init__(type_name, field, endianness)

    def cpp_type(self):
        return 'bool'

    def default_value(self):
        return 'false'

    def builder_serialize_body(self):
        assert self._field.offset_in_capture is not None
        return f'''if({self._field.name}_)
        {{
            *reinterpret_cast<{self.capture_type}*>(sink + {self._dynamic_offset} {self.offset_name()}) |= (1<<{self._field.offset_in_capture});
        }}
        else
        {{
            *reinterpret_cast<{self.capture_type}*>(sink + {self._dynamic_offset} {self.offset_name()}) &= ~(1<<{self._field.offset_in_capture});
        }}
        '''

    def _add_shift(self):
        return ""

    def _add_mask(self):
        return ""

    def _add_return(self):
        assert self._field.offset_in_capture is not None
        return f'return (capture_type & (1<<{self._field.offset_in_capture})) == (1<<{self._field.offset_in_capture});'

    def to_string_code(self, string_stream_var_name):
        return f'{string_stream_var_name} << ({self._field.name}() ? "set" : "cleared");'

    def validation_code(self, variable_name):
        # We don't ned validation for the flag because a bool can't be anything other than true or false
        # error
        return ""