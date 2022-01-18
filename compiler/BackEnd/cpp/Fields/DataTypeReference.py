from BackEnd.cpp.Fields.Field import Field
from Model.Field import Field as ModelField

class DataTypeReference(Field):
    def __init__(self, type_name:str, field:ModelField, endianness:str, settings):
        self._referenced_type = field.type().referenced_type()
        self._cpp17 = settings.cpp17
        super().__init__(type_name, field, endianness)
        self._builder_cpp_type = f"{self._field.type()._name.replace('.','::')}_builder"

    def cpp_type(self):
        if self._cpp17:
            return f"const {self._field.type()._name.replace('.','::')}_view&"
        else:
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
        if self._cpp17:
            return f'''if(!{self._field.name}_)
    {self._field.name}_ = {self._referenced_type.identifier}_view(data_ + {self._dynamic_offset}{self.offset_name()});
return *{self._field.name}_;'''
        else:
            return f'return {self._referenced_type.identifier}_view(data_ + {self._dynamic_offset}{self.offset_name()});'

    def builder_serialize_body(self):
        return f'{self._field.name}_.build(sink + {self._dynamic_offset}{self.offset_name()});\n'

    def builder_parameter_code(self):
        return f'{self._builder_cpp_type} {self._field.name}'

    def builder_field_code(self):
        return f'{self._builder_cpp_type} {self._field.name}_ = {self.default_value()};'

    def builder_setter_code(self):
        return \
        f'''void {self._field.name}({self._builder_cpp_type} val) 
        {{ 
            {self._field.name}_ = val; 
        }}'''

    def builder_getter_code(self):
        return f'''const {self._builder_cpp_type}& {self._field.name}() const
        {{
            return {self._field.name}_;
        }}'''

    def is_datatype(self):
        return True

    def includes(self):
        return ['<optional>'] if self._cpp17 else []

    def cache_field(self):
        # String slicing in the return type is an ugle hack to go from const T & to T
        return f'mutable std::optional<{self.cpp_type()[6:-1]}> {self._field.name}_;' if self._cpp17 else None