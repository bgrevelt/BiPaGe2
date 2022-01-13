import math
import re

# Returns the nearest larger standard type for a number of bits.
# e.g. 3 -> 8, 5 -> 8, 9 -> 16, etc.
def to_standard_size(size):
    bytes_required = math.ceil(size / 8)
    bytes_nearest_type = 2 ** (math.ceil(math.log(bytes_required, 2)))
    return bytes_nearest_type * 8

# Split a sized type (e.g. uint32) into the type and the size (e.g uint and 32)
def split_sized_type(type):
    typename = "".join([c for c in type if not c.isnumeric()])
    size = int("".join([c for c in type if c.isnumeric()]))
    return typename,size

# s*, u*, and f* are aliases for int*, uint*, and float* respectively.
def is_aliased_type(type):
    return re.search("^[s,u,f]\d{1,2}$",type) is not None

# Takes an alias type (e.g. s*, u*, or f*) and returns the 'real' type name (e.g. int*, uint*, or float*)
def remove_aliases(type):
    aliases = {
        'u': 'uint',
        's': 'int',
        'f': 'float'
    }
    if is_aliased_type(type):
        return aliases[type[0]] + type[1:]
    else:
        return type