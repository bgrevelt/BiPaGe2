import os


type_conversion_table = {
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

type_default_table = {
    'uint8': '0',
    'u8': '0',
    'uint16': '0',
    'u16': '0',
    'uint32': '0',
    'u32': '0',
    'uint64': '0',
    'u64': '0',
    'int8': '0',
    's8': '0',
    'int16': '0',
    's16': '0',
    'int32': '0',
    's32': '0',
    'int64': '0',
    's64': '0',
    'float32': '0.f',
    'f32': '0.f',
    'float64': '0.',
    'f64': '0.'
}

def TypeToCppType(Type):
    return type_conversion_table[Type]

def GetTypeDefaultValue(Type):
    return type_default_table[Type]

def FieldOffsetName(Field):
    name = Field.name.upper()
    return f"{name}_OFFSET"