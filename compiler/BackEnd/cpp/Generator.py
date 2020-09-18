import os

class Generator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.type_conversion_table = {
            'uint8': 'std::uint8_t',
            'u8': 'std::uint8_t',
            'uint16': 'std::uint16_t',
            'u16': 'std::uint16_t',
            'uint32': 'std::uint32_t',
            'u32': 'std::uint32_t',
            'uint64': 'std::uint64_t',
            'u64': 'std::uint64_t',
            'int8': 'std::int8_t',
            's8': 'std::int8_t',
            'int16': 'std::int16_t',
            's16': 'std::int16_t',
            'int32': 'std::int32_t',
            's32': 'std::int32_t',
            'int64': 'std::int64_t',
            's64': 'std::int64_t',
            'float32': 'float',
            'f32': 'float',
            'float64': 'double',
            'f64': 'double'
        }

    def Generate(self, model):
        for DataType in model:
            self.GenerateDataTypeParser(DataType)

    def GenerateDataTypeParser(self, DataType):
        headerpath = os.path.join(self.output_dir, f"{DataType.identifier}_generated.h")
        sourcepath = os.path.join(self.output_dir, f"{DataType.identifier}_generated.cpp")
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        with open(headerpath, 'w+') as header, open(sourcepath, 'w+') as source:
            self.WriteDataTypeHeader(DataType, header)

    def WriteDataTypeHeader(self, DataType, header):
        template = '''#include <cstdint>

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
    
    const {view}& Parse{typename}(const std::uint8_t& data) 
    {{ 
        return reinterpret_cast<const {view}&>(data);
    }}

}}
'''
        offsets = "\n\t".join(self.GetOffsets(DataType.fields))
        fields = "\n".join([self.GetFieldGetter(field) for field in DataType.fields])
        header.write(template.format(offsets = offsets, typename = DataType.identifier, fields = fields, view=f'{DataType.identifier}_view'))

    def WriteGetters(self, Fields, header):
        for field in Fields:
            self.WriteGetter(field, header)

    def GetFieldGetter(self, Field):
        template = '''
        {type} {fieldname}() const
        {{
            return *reinterpret_cast<const {type}*>(&data_ + {offset});
        }}'''
        return template.format(type = self.TypeToCppType(Field.type), fieldname=Field.name, offset=self.FieldOffsetName(Field))

    def GetOffsets(self, Fields):
        return [f"#define {self.FieldOffsetName(field)} {field.offset}" for field in Fields]

    def FieldOffsetName(self, Field):
        name = Field.name.upper()
        return f"{name}_OFFSET"

    def TypeToCppType(self, Type):
        return self.type_conversion_table[Type]