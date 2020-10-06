from .Fields import factory as field_factory
from .Beautifier import *
import math


class DataType:
    def __init__(self, datatype, settings):
        self._settings = settings
        self._fields = [field_factory.create(field, settings) for field in datatype.fields]
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
}};
'''
    def generate(self, path):
        with open(path, 'w+') as f:
            f.write(self._beautifier.beautify(
                f'''{ self.includes()}
    
                namespace BiPaGe
                {{
                {self.defines()}
    
                {self.parser_code()}
    
                {self.builder_code()}
    
                }}
                '''
            ))

    def includes(self):
        incs = ['<cstdint>', '<assert.h>', '<vector>']
        if self._settings.cpp_validate_input:
            incs.append('<string>') # needed for std::to_string
        return '\n'.join(f'#include {include}' for include in incs)

    def defines(self):
        return '\n'.join([f'#define {key} {value}' for field in self._fields for key, value in field.defines()])

    def parser_code(self):
        fields = "\n\n".join([field.view_getter_code() for field in self._fields])
        return \
            '''class {typename}_view
            {{
            public:
                // You should not create or copy this class as it's just a view on raw data
                // Creating or copying this class will give you a class with one byte of data.
                {typename}_view() = delete;
                ~{typename}_view() = delete;
                {typename}_view(const {typename}_view&) = delete;
                {typename}_view& operator=(const {typename}_view&) = delete;
    
                {fields}
    
            private:
                const std::uint8_t data_;
            }};
    
            const {typename}_view& Parse{typename}(const std::uint8_t* data) 
            {{ 
                assert(data);
                return reinterpret_cast<const {typename}_view&>(*data);
            }}
            '''.format(typename=self._identifier, fields=fields)

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
                                    fields=fields)

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
        body = "".join([field.builder_serialize_code() for field in self._fields])

        return \
            f'''void build(uint8_t * sink) const // serialize the data to the given buffer
            {{
            {body.rstrip()}
            }}
            '''

    def _builder_size(self):
        size = math.ceil(self._datatype.size_in_bits() / 8 )
        return \
            f'''size_t size() const // return the size of the serialized data
            {{
                return {size};
            }}'''
