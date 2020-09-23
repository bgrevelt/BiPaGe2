from .HelperFunctions import *

class ViewGenerator:

    def GenerateDataTypeParser(self, DataType):
        template = '''class {typename}_view
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
'''
        fields = "\n".join([self.GetFieldGetter(field) for field in DataType.fields])
        return template.format(typename=DataType.identifier, fields=fields)


    def GetFieldGetter(self, Field):
        template = '''
    {type} {fieldname}() const
    {{
        return *reinterpret_cast<const {type}*>(&data_ + {offset});
    }}'''
        return template.format(type=TypeToCppType(Field.type), fieldname=Field.name,
                               offset=FieldOffsetName(Field))

    def GetIncludes(self):
        return ['<cstdint>', '<assert.h>']