from BackEnd.cpp.Fields.Integer import Integer
from Model.Field import Field as ModelField

class Flag(Integer):
    def __init__(self, type_name:str, field:ModelField, endianness:str, settings):
        super().__init__(type_name, field, endianness, settings)

    def cpp_type(self):
        return 'bool'

    def default_value(self):
        return 'false'

    def base_type(self):
        return Integer.to_cpp_type(8, False)

    def builder_serialize_code(self):
        offset_in_capture = (self._field.offset - self._field.capture_offset)
        return f'''if({self._field.name}_)
        {{
            *reinterpret_cast<{self.capture_type}*>(sink + {self._offset_name()}) |= (1<<{offset_in_capture});
        }}
        else
        {{
            *reinterpret_cast<{self.capture_type}*>(sink + {self._offset_name()}) &= ~(1<<{offset_in_capture});
        }}
        '''

    def _add_shift(self):
        return ""

    def _add_mask(self):
        return ""

    def _add_return(self):
        offset_in_capture = (self._field.offset - self._field.capture_offset)
        return f'return (capture_type & (1<<{offset_in_capture})) == (1<<{offset_in_capture});'

    def to_string_code(self):
        return f'({self._field.name}() ? "set" : "cleared")'

    def validation_code(self, variable_name):
        # We don't ned validation for the flag because a bool can't be anything other than true or false
        # error
        return ""