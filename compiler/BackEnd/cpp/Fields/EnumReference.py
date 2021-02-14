from BackEnd.cpp.Fields.Integer import Integer
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
        enum_name = field.type().referenced_type().name()
        first_enumerator_name = field.type().referenced_type().enumerators()[0][0]
        default = f'{enum_name}::{first_enumerator_name}'


        super().__init__(type_name, field, endianness, settings, default)

        self._cpp_type = field.type()._name