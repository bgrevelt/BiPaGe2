from .HelperFunctions import *
import unittest
import math
from .Fields import factory

class BuilderGenerator:
    def __init__(self):
        self.template = \
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

    def GetIncludes(self):
        return ['<cstdint>', '<assert.h>', '<vector>']

    def GenerateBuilder(self, DataType):
        fields = [factory.Build(f) for f in DataType.fields]
        return self.template.format(typename=DataType.identifier,
                                    ctor=self.GenerateCtor(DataType),
                                    setters=self.GenerateSetters(fields),
                                    getters=self.GenerateGetters(fields),
                                    pointer_build=self.GeneratreBuilderFunction(fields),
                                    size=self.GenerateSizeFunction(DataType),
                                    fields=self.GenerateFields(DataType))

    def GenerateCtor(self, DataType):
        ctor_template = \
'''{typename}_builder( // ctor that sets all fields to the specified value
{parameters})
{initializers}
{{
}}'''

        parameters = ",\n".join([f'{TypeToCppType(field.type, field.encapsulating_type_size())} {field.name}' for field in DataType.fields])
        initializers = ": " + "\n, ".join([f'{field.name}_({field.name})' for field in DataType.fields])
        #initializers = ':' + initializers[1:]

        return ctor_template.format(typename=DataType.identifier,
                                    parameters=parameters,
                                    initializers=initializers)

    def GenerateFields(self, DataType):
        return "\n".join([f'{TypeToCppType(field.type, field.encapsulating_type_size())} {field.name}_ = {GetTypeDefaultValue(field.type)};' for field in DataType.fields])

    def GenerateSetters(self, fields):
        return '\n'.join([field.builder_setter_code() for field in fields])

    def GenerateGetters(self, fields):
        return '\n'.join([field.builder_getter_code() for field in fields])

    def GeneratreBuilderFunction(self, fields):
        body = "\n".join([field.builder_serialize_code() for field in fields])

        return f'''void build(uint8_t * sink) const // serialize the data to the given buffer
{{
{body}
}}
'''
      
    def GenerateSizeFunction(self, DataType):
        last_field = DataType.fields[-1]
        size = math.ceil((last_field.offset + last_field.size_in_bits) / 8 )
        return \
f'''size_t size() const // return the size of the serialized data
{{
    return {size};
}}'''


