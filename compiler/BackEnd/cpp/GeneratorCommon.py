import os


class GeneratorCommon:
    def __init__(self):
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

    def TypeToCppType(self, Type):
        return self.type_conversion_table[Type]

    def GetOffsets(self, Fields):
        return [f"#define {self.FieldOffsetName(field)} {field.offset}" for field in Fields]

    def FieldOffsetName(self, Field):
        name = Field.name.upper()
        return f"{name}_OFFSET"