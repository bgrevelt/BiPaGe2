from .Float import Float32
from .Float import Float64
from .Integer import Integer

def create(field, settings):
    if field.type == 'int' or field.type == 'uint':
        return Integer(field, settings)
    elif field.type == 'float':
        if field.size_in_bits == 32:
            return Float32(field, settings)
        else:
            assert field.size_in_bits == 64, "unknown size for float type: {}".format(field.size_in_bits)
            return Float64(field, settings)
    else:
        assert False, "Unknown type {} and length {}".format(field.type, field.size_in_bits)