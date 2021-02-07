from .Float import Float32
from .Float import Float64
from .Integer import Integer
from Model.Types.Integer import Integer as IntType
from Model.Types.Float import Float as FloatType

def create(field, endianness, settings):
    a = IntType(5, False, None)
    test = type(a) is IntType
    if type(field._type) is IntType:
        return Integer(field, endianness, settings)
    elif type(field._type) is FloatType:
        if field.size_in_bits() == 32:
            return Float32(field, endianness, settings)
        else:
            assert field.size_in_bits() == 64, "unknown size for float type: {}".format(field.size_in_bits)
            return Float64(field, endianness, settings)
    else:
        assert False, "Unknown type {} and length {}".format(field, field.size_in_bits())