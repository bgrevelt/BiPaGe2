class Field:
    def __init__(self, field, cpp_type, default_value, settings):
        self._field = field
        self._settings = settings
        self._cpp_type = cpp_type
        self._default_value = default_value
        self._getter_template =\
        '''{type} {fieldname}() const
        {{
            {body}
        }}'''

    def name(self):
        return self._field.name

    def view_getter_code(self):
        return f'''{self._cpp_type} {self._field.name}() const
                {{
                    return *reinterpret_cast<const {self._cpp_type}*>(&data_ + {self._offset_name()});
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
        return f'*reinterpret_cast<{self._cpp_type}*>(sink + {self._offset_name()}) = {self._field.name}_;\n'

    def builder_parameter_code(self):
        # std::uintt_t foo
        return f'{self._cpp_type} {self._field.name}'

    def builder_initializer_code(self):
        # foo_(foo)
        return f'{self._field.name}_({self._field.name})'


    def builder_field_code(self):
        # std::uint8_t foo_ = 0;
        return f'{self._cpp_type} {self._field.name}_ = {self._default_value};'

    # Return key value pairs. They will be tured into #define {key} {value}
    def defines(self):
        return [(self._offset_name(), (self._field.offset // 8))]

    def _offset_name(self):
        name = self._field.name.upper()
        return f"{name}_OFFSET"

    def validation_code(self, variable_name):
        return ""