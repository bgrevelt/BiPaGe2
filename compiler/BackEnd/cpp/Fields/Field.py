from abc import ABC, abstractmethod

class Field(ABC):
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
        self._dynamic_offset = f'GetEndOf{self._field.dynamic_capture_offset().name}() + ' if self._field.dynamic_capture_offset() is not None else ""

    @abstractmethod
    def getter_body(self):
        pass

    @abstractmethod
    def cpp_type(self):
        pass

    @abstractmethod
    def builder_serialize_body(self):
        pass

    @abstractmethod
    def default_value(self):
        pass

    @abstractmethod
    def to_string_code(self, string_stream_var_name):
        pass

    def add_swap_if_required(self, statement):
        if self._endianness == 'big' and self._field.size_in_bits() != 8:
            return f'BiPaGe::swap_bytes({statement})'
        else:
            return statement

    def name(self):
        return self._field.name

    def view_getter_code(self):
        return_type = self.cpp_type();
        method_name = self._field.name
        method_body = self.getter_body()
        return f'''{return_type} {method_name}() const
        {{
            {method_body}
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
        return [(self.offset_name(), (self._field.static_capture_offset() // 8))]

    def offset_name(self):
        typename = self._type_name.upper()
        name = self._field.name.upper()
        return f"{typename}_{name}_CAPTURE_OFFSET"

    def validation_code(self, variable_name):
        return ""

    def includes(self):
        return []

    def dynamic_capture_offset(self):
        from BackEnd.cpp.Fields.factory import create # ugly hack to get around circular dependency
        offset = self._field.dynamic_capture_offset()
        if offset is None:
            return None
        else:
            return create(self._type_name, offset, self._endianness, None)

    def has_static_size(self):
        return not self._field.size_in_bits() is None

    def capture_size(self):
        return self._field.capture_size()

    def is_collection(self):
        return False

    def is_datatype(self):
        return False

    def cache_field(self):
        return None