import os

type_default_table = {
    'uint': '0',
    'int': '0',
    'float': '0.0'
   }

def TypeToCppType(type, size):
    if type == 'int':
        return f'std::int{size}_t'
    elif type == 'uint':
        return f'std::uint{size}_t'
    elif type == 'float' and size == 32:
        return 'float'
    elif type == 'float' and size == 64:
        return 'double'

def GetTypeDefaultValue(type):
    return type_default_table[type]

def FieldOffsetName(Field):
    name = Field.name.upper()
    return f"{name}_OFFSET"