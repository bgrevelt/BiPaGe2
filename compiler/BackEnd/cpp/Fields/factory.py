from .Float import Float32
from .Float import Float64
from .Integer import Integer
from Model.Types.Integer import Integer as IntType
from Model.Types.Float import Float as FloatType
from Model.Types.Reference import Reference

def create(type_name, field, endianness, settings):
    if type(field.type()) is IntType:
        return Integer(type_name,field, endianness, settings)
    elif type(field.type()) is FloatType:
        if field.size_in_bits() == 32:
            return Float32(type_name, field, endianness, settings)
        else:
            assert field.size_in_bits() == 64, "unknown size for float type: {}".format(field.size_in_bits)
            return Float64(type_name, field, endianness, settings)
    elif type(field.type()) is Reference:
        # TODO: temporary hack
        return Integer(type_name, field, endianness, settings)
    else:
        assert False, "Unknown type {} and length {}".format(field, field.size_in_bits())