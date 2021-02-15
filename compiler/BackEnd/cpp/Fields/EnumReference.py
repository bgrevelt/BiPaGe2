from BackEnd.cpp.Fields.Integer import Integer
from BackEnd.cpp.Fields.Integer import _to_cpp_type
from Model.Field import Field as ModelField
'''
Interface for Field
defines()
view_getter_code()
builder_field_code()
builder_setter_code()
builder_getter_code()
builder_parameter_code()
builder_initializer_code()
name()
builder_serialize_code()
'''

class EnumReference(Integer):
    def __init__(self, type_name:str, field:ModelField, endianness:str, settings):
        self._enum_name = field.type().referenced_type().name()
        self._field = field
        first_enumerator_name = field.type().referenced_type().enumerators()[0][0]
        default = f'{self._enum_name}::{first_enumerator_name}'


        super().__init__(type_name, field, endianness, settings, default)

        self._cpp_type = field.type()._name

    def view_getter_code(self):
        if not self._scoped:
            return super().view_getter_code()

        fieldname = self._field.name
        return_type = self._field.type()._name
        body = self._body()

        return f'''{return_type} {fieldname}() const
        {{
            {body}
        }}'''

    def _add_return(self):
        return_type = self._field.type()._name

        if self._field.capture_size != self._field.standard_size:
            return f'return static_cast<{return_type}>(capture_type);'
        else:
            return 'return capture_type;'

    def builder_serialize_code(self):
        if not self._scoped:
            return super().builder_serialize_code()

        offset_in_byte = (self._field.offset - self._field.capture_offset)
        mask = (2 ** self._field.size_in_bits() - 1) << offset_in_byte  # mask should not include sign bit

        base_standard_cpp_type = _to_cpp_type(self._field.type().referenced_type().standard_size(), self._field.type().referenced_type().signed())
        r = f'{self.capture_type} {self._field.name} = static_cast<{base_standard_cpp_type}>({self._field.name}_);\n'
        if offset_in_byte != 0:
            r += f'{self._field.name} <<= {offset_in_byte};\n'

        r += f'{self._field.name} &= 0x{mask:x};\n'

        # Note: byte swapping for big endian types happens at the datatype level so we can swap the
        # entire capture scope at once

        r += f'*reinterpret_cast<{self.capture_type}*>(sink + {self._offset_name()}) |= {self._field.name};\n\n'
        return r