class Field:
    def __init__(self, type_name, field, endianness):
        self._type_name = type_name
        self._field = field
        self._endianness = endianness
        self._cpp_type = self.cpp_type()
        self._getter_template =\
        '''{type} {fieldname}() const
        {{
            {body}
        }}'''

    def name(self):
        return self._field.name

    def view_getter_code(self):
        if self._endianness == 'little' or self._field.size_in_bits() == 8:
            return f'''{self._cpp_type} {self._field.name}() const
                    {{
                        return *reinterpret_cast<const {self._cpp_type}*>(data_ + {self._offset_name()});
                    }}'''
        else:
            return f'''{self._cpp_type} {self._field.name}() const
                    {{
                        return BiPaGe::swap_bytes(*reinterpret_cast<const {self._cpp_type}*>(data_ + {self._offset_name()}));
                    }}'''

    def builder_setter_code(self):
        return \
        f'''void {self._field.name}({self._cpp_type} val) 
        {{ 
            {self._field.name}_ = val; 
        }}'''

    def builder_getter_code(self):
        return f'''{self._cpp_type} {self._field.name}() const
        {{
            return {self._field.name}_;
        }}'''

    def builder_serialize_code(self):
        if self._endianness == 'little' or self._field.size_in_bits() == 8:
            return f'*reinterpret_cast<{self._cpp_type}*>(sink + {self._offset_name()}) = {self._field.name}_;\n'
        else:
            return f'*reinterpret_cast<{self._cpp_type}*>(sink + {self._offset_name()}) = BiPaGe::swap_bytes({self._field.name}_);\n'

    def builder_parameter_code(self):
        # std::uintt_t foo
        return f'{self._cpp_type} {self._field.name}'

    def builder_initializer_code(self):
        # foo_(foo)
        return f'{self._field.name}_({self._field.name})'


    def builder_field_code(self):
        # std::uint8_t foo_ = 0;
        return f'{self._cpp_type} {self._field.name}_ = {self.default_value()};'

    # Return key value pairs. They will be tured into #define {key} {value}
    def defines(self):
        return [(self._offset_name(), (self._field.capture_offset // 8))]

    def _offset_name(self):
        typename = self._type_name.upper()
        name = self._field.name.upper()
        return f"{typename}_{name}_CAPTURE_OFFSET"

    def validation_code(self, variable_name):
        return ""

    # Method can be overridden if the field needs to do some prep work to represent itself as a string
    def to_string_prep(self):
        return None

    def to_string_code(self):
        return f'{self._field.name}()'

    def includes(self):
        return []