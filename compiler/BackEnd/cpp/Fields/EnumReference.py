from BackEnd.cpp.Fields.Integer import Integer
from Model.Field import Field as ModelField

class EnumReference(Integer):
    def __init__(self, type_name:str, field:ModelField, endianness:str, settings):
        self._referenced_enum = field.type().referenced_type()
        self._field = field
        super().__init__(type_name, field, endianness, settings)

    def cpp_type(self):
        return self._field.type()._name

    def default_value(self):
        # We have to set the variable to something in the default constructor of the builder
        # only sensible thing to do seems to be to use the first enumerator
        enumeration_name = self._referenced_enum.name()
        first_enumerator_name, _ = self._referenced_enum.enumerators()[0]
        return f'{enumeration_name}::{first_enumerator_name}'

    def base_type(self):
        return Integer.to_cpp_type(self._referenced_enum.standard_size(), self._referenced_enum.signed())

    def to_string_code(self):
        return f'enum_to_string({self._field.name}())'