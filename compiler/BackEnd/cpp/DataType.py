from .Fields import factory as field_factory
from .Beautifier import *
import math


class DataType:
    def __init__(self, datatype, endianness, settings):
        self._endianness = endianness
        self._settings = settings
        self._fields = [field_factory.create(datatype.identifier, field, endianness, settings) for field in datatype.fields]
        self._datatype = datatype
        self._identifier = datatype.identifier
        self._beautifier = Beautifier()
        self._builder_template = \
'''
class {typename}_builder
{{
public:
    {typename}_builder() = default; 
    {ctor}
    
    {setters}
    
    {getters}
    
    {pointer_build}
    
    std::vector<std::uint8_t> build() const
    {{
        std::vector<uint8_t> data(size());
        build(data.data());
        return data;
    }}
    
{size}

private:
    {fields}
    {dynamic_offsets}
}};
'''

    def includes(self):
        incs = ['<cstdint>', '<assert.h>', '<vector>']
        if self._settings.cpp_validate_input:
            incs.append('<string>') # needed for std::to_string
        if self._endianness == 'big':
            incs.append('<BiPaGe/Endianness.h>')  # Contains functions to translate from big to little endianness
        if self._settings.cpp_to_string:
            incs.extend(['<sstream>', '<iomanip>'])

        incs.extend([inc for field in self._fields for inc in field.includes()])

        return [f'#include {include}' for include in incs]

    def defines(self):
        return [f'#define {key} {value}' for field in self._fields for key, value in field.defines()]

    def parser_code(self):
        fields = "\n\n".join([field.view_getter_code() for field in self._fields])
        return \
            '''class {typename}_view
            {{
            public:
                {typename}_view(const std::uint8_t* data)
                : data_(data)
                {{
                }}
                ~{typename}_view() {{}}
    
                {fields}
                
                {tostring}
    
            private:
                const std::uint8_t* data_;
                {dynamic_offsets}
            }};
            '''.format(typename=self._identifier, fields=fields, tostring=self.to_string_code(), dynamic_offsets=self._view_dynamic_offsets())

    def builder_code(self):
        fields = '\n'.join([field.builder_field_code() for field in self._fields])
        setters = '\n'.join([field.builder_setter_code() for field in self._fields])
        getters = '\n'.join([field.builder_getter_code() for field in self._fields])
        return self._builder_template.format(typename=self._identifier,
                                    ctor=self._builder_ctor(),
                                    setters=setters,
                                    getters=getters,
                                    pointer_build=self._builder_build_method(),
                                    size=self._builder_size(),
                                    fields=fields,
                                    dynamic_offsets=self._builder_dynamic_offsets())

    def _builder_ctor(self):
        parameters = ",\n".join([field.builder_parameter_code() for field in self._fields])
        initializers = ": " + "\n, ".join([field.builder_initializer_code() for field in self._fields])
        validation = "\n".join(field.validation_code(field.name()) for field in self._fields) if self._settings.cpp_validate_input else ""

        return \
        f'''{self._identifier}_builder( // ctor that sets all fields to the specified value
        {parameters})
        {initializers}
        {{
            {validation}
        }}'''

    def _builder_build_method(self):
        body = "".join([field.builder_serialize_body() for field in self._fields])

        r = \
            f'''void build(uint8_t * sink) const // serialize the data to the given buffer
            {{
            {body.rstrip()}
            '''

        if self._endianness == 'big':
            r += '''
            // Byte swap all capture scopes.\n'''
            for i, capture_scope in enumerate(self._datatype.capture_scopes):
                # TODO: code duplication. We should really add the capture scope to the backend model
                # to prevent this instead of using hacky solutions like this.
                offset_name = f'{self._identifier.upper()}_{capture_scope.fields()[0].name.upper()}_CAPTURE_OFFSET'
                r += f'auto capture_scope_{i+1} = reinterpret_cast<std::uint{capture_scope.size()}_t*>(sink + {offset_name});\n'
                r += f'*capture_scope_{i+1} = BiPaGe::swap_bytes(*capture_scope_{i+1});\n'

        r += '}'
        return r

    def to_string_prep(self):
        return "\n".join(field.to_string_prep() for field in self._fields if field.to_string_prep() is not None)

    def to_string_code(self):
        if not self._settings.cpp_to_string:
            return ""

        longest_field_name = max(len(field.name) for field in self._datatype.fields)

        r = f'''std::string to_string() const
    {{  
        std::stringstream ss;
        
        '''

        for field in self._fields:
            r += f'ss << std::setw({longest_field_name + 2}) << "{field.name()}: ";'
            r += field.to_string_code('ss')
            r += 'ss << std::endl;\n'

        r+= '''
        return ss.str();
        }'''

        return r


    def _builder_size(self):
        size = None
        if self._datatype.size_in_bits() is not None: # static size
            size = str(math.ceil(self._datatype.size_in_bits() / 8))
        else:
            size = str(math.ceil(self._datatype.static_size_in_bits() / 8))
            dynamic_fields = {field.dynamic_capture_offset() for field in self._datatype.fields if field.dynamic_capture_offset() is not None}
            dynamic_fields = [f'{field.name}_.size() * sizeof(decltype ({field.name}_)::value_type)' for field in dynamic_fields]
            size = size + '+ ' + ' + '.join(dynamic_fields)

        return \
            f'''size_t size() const // return the size of the serialized data
            {{
                return {size};
            }}'''

    def _get_dynamic_offsets(self):
        offset_names = {field.dynamic_capture_offset().name() for field in self._fields if
                        field.dynamic_capture_offset() is not None}
        return [field for field in self._fields if field.name() in offset_names]

    def _view_dynamic_offsets(self):
        getters = []
        indexes = []

        for offset in self._get_dynamic_offsets():
            offset_dynamic_offset = f'GetEndOf{offset.dynamic_capture_offset().name()}() +' if offset.dynamic_capture_offset() is not None else ""
            offset_static_offset = offset.offset_name()
            getters.append(f'''size_t GetEndOf{offset.name()}() const
            {{
                if(end_of_{offset.name()}_ == 0)
                    end_of_{offset.name()}_ = {offset_dynamic_offset} {offset_static_offset} + {offset.name()}().size_in_bytes();
        
                return end_of_{offset.name()}_;
            }}''')

            indexes.append(f'mutable size_t end_of_{offset.name()}_ = 0;')

        getters = '\n'.join(getters)
        indexes = '\n'.join(indexes)
        return getters + '\n' + indexes

    def _builder_dynamic_offsets(self):
        getters = []
        indexes = []

        for offset in self._get_dynamic_offsets():
            offset_dynamic_offset = f'GetEndOf{offset.dynamic_capture_offset().name()}() +' if offset.dynamic_capture_offset() is not None else ""
            offset_static_offset = offset.offset_name()
            getters.append(f'''size_t GetEndOf{offset.name()}() const
            {{
                if(end_of_{offset.name()}_ == 0)
                    end_of_{offset.name()}_ = {offset_dynamic_offset} {offset_static_offset} + {offset.name()}_.size() * sizeof(decltype ({offset.name()}_)::value_type);

                return end_of_{offset.name()}_;
            }}''')

            indexes.append(f'mutable size_t end_of_{offset.name()}_ = 0;')

        getters = '\n'.join(getters)
        indexes = '\n'.join(indexes)
        return getters + '\n' + indexes
