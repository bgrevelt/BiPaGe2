from .HelperFunctions import *
import unittest

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
        return self.template.format(typename=DataType.identifier,
                                    ctor=self.GenerateCtor(DataType),
                                    setters=self.GenerateSetters(DataType),
                                    getters=self.GenerateGetters(DataType),
                                    pointer_build=self.GeneratreBuilderFunction(DataType),
                                    size=self.GenerateSizeFunction(DataType),
                                    fields=self.GenerateFields(DataType))

    def GenerateCtor(self, DataType):
        ctor_template = \
'''{typename}_builder( // ctor that sets all fields to the specified value
{parameters})
{initializers}
{{
}}'''

        parameters = ",\n".join([f'{TypeToCppType(field.type)} {field.name}' for field in DataType.fields])
        initializers = ": " + "\n, ".join([f'{field.name}_({field.name})' for field in DataType.fields])
        #initializers = ':' + initializers[1:]

        return ctor_template.format(typename=DataType.identifier,
                                    parameters=parameters,
                                    initializers=initializers)

    def GenerateFields(self, DataType):
        return "\n".join([f'{TypeToCppType(field.type)} {field.name}_ = {GetTypeDefaultValue(field.type)};' for field in DataType.fields])

    def GenerateSetters(self, DataType):
        return '\n'.join([self.GenerateSetter(field) for field in DataType.fields])

    def GenerateSetter(self, field):
        return \
f'''void {field.name}({TypeToCppType(field.type)} val) 
{{ 
    {field.name}_ = val; 
}}'''

    def GenerateGetters(self, DataType):
        return '\n'.join([self.GenerateGetter(field) for field in DataType.fields])

    def GenerateGetter(self, field):
        return \
f'''{TypeToCppType(field.type)} {field.name}() const
{{
    return {field.name}_;
}}'''

    def GeneratreBuilderFunction(self, DataType):
        r = \
'''void build(uint8_t * sink) const // serialize the data to the given buffer
{
'''
        for n, field in enumerate(DataType.fields):
            r+= f'*reinterpret_cast<{TypeToCppType(field.type)}*>(sink + {FieldOffsetName(field)}) = {field.name}_;\n'

        r += '\t}'
        return r

    def GenerateSizeFunction(self, DataType):
        last_field = DataType.fields[-1]
        size = last_field.offset + last_field.size()
        return \
f'''size_t size() const // return the size of the serialized data
{{
    return {size};
}}'''


