from BackEnd.cpp.Fields.Integral import Integral
from compiler.Model.Field import Field as ModelField

class EnumReference(Integral):
    def __init__(self, type_name:str, field:ModelField, endianness:str, settings):
        self._referenced_enum = field.type().referenced_type()
        self._field = field
        super().__init__(type_name, field, endianness)

    def cpp_type(self):
        return self._field.type()._name.replace('.','::')

    def default_value(self):
        # We have to set the variable to something in the default constructor of the builder
        # only sensible thing to do seems to be to use the first enumerator
        first_enumerator_name, _ = self._referenced_enum.enumerators()[0]
        return f'{self.cpp_type()}::{first_enumerator_name}'

    def base_type(self):
        return self._to_cpp_type(self._referenced_enum.standard_size(), self._referenced_enum.signed())

    def to_string_code(self, string_stream_var_name):
        return f'{string_stream_var_name} << enum_to_string({self._field.name}());'

    def validation_code(self, variable_name):
        # We don't ned validation for the enumeration because they're limited to the values
        # contained in the enumeration by nature. Sure, someone can static_cast a value that's
        # not part of the enumeration, but I don't think we need to guard for that type of programmer
        # error
        return ""