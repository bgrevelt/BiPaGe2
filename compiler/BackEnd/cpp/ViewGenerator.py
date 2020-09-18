from .GeneratorCommon import GeneratorCommon
import os

class ViewGenerator(GeneratorCommon):

    def GenerateDataTypeParser(self, DataType):
        template = '''#include <cstdint>
#include <assert.h>

namespace BiPaGe
{{
    {offsets}

    class {view}
    {{
    public:
        // You should not create or copy this class as it's just a view on raw data
        // Creating or copying this class will give you a class with one byte of data.
        {view}() = delete;
        ~{view}() = delete;
        {view}(const {view}&) = delete;
        {view}& operator=(const {view}&) = delete;

        {fields}

    private:
        const std::uint8_t data_;
    }};

    const {view}& Parse{typename}(const std::uint8_t* data) 
    {{ 
        assert(data);
        return reinterpret_cast<const {view}&>(*data);
    }}

}}
'''
        offsets = "\n\t".join(self.GetOffsets(DataType.fields))
        fields = "\n".join([self.GetFieldGetter(field) for field in DataType.fields])
        return template.format(offsets=offsets, typename=DataType.identifier, fields=fields,
                                     view=f'{DataType.identifier}_view')


    def GetFieldGetter(self, Field):
        template = '''
        {type} {fieldname}() const
        {{
            return *reinterpret_cast<const {type}*>(&data_ + {offset});
        }}'''
        return template.format(type=self.TypeToCppType(Field.type), fieldname=Field.name,
                               offset=self.FieldOffsetName(Field))