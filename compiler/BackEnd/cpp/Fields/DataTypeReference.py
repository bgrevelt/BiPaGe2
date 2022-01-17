from BackEnd.cpp.Fields.Field import Field
from Model.Field import Field as ModelField

class DataTypeReference(Field):
    def __init__(self, type_name:str, field:ModelField, endianness:str, settings):
        self._referenced_type = field.type().referenced_type()
        super().__init__(type_name, field, endianness)
        self._builder_cpp_type = f"{self._field.type()._name.replace('.','::')}_builder"

    def cpp_type(self):
        return f"{self._field.type()._name.replace('.','::')}_view"

    def default_value(self):
        return '{}'

    def to_string_code(self, string_stream_var_name):
        return f'{string_stream_var_name} << std::endl << "{{" << std::endl ' \
               f'<< {self._field.name}().to_string() << std::endl ' \
               f'<< "}}";'

    def validation_code(self, variable_name):
        # No validation necessary. That's up to the type
        return ""

    def getter_body(self):
        return f'return {self._referenced_type.identifier}_view(data_ + {self._dynamic_offset}{self.offset_name()});'

    def builder_serialize_body(self):
        return ''

    def builder_parameter_code(self):
        # std::uintt_t foo
        return f'{self._builder_cpp_type} {self._field.name}'

    def builder_field_code(self):
        # std::uint8_t foo_ = 0;
        return f'{self._builder_cpp_type} {self._field.name}_ = {self.default_value()};'

    def builder_setter_code(self):
        return \
        f'''void {self._field.name}({self._builder_cpp_type} val) 
        {{ 
            {self._field.name}_ = val; 
        }}'''

    def builder_getter_code(self):
        return f'''{self._builder_cpp_type} {self._field.name}() const
        {{
            return {self._field.name}_;
        }}'''