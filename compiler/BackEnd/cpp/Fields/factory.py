from BackEnd.cpp.Fields.Float import Float32
from BackEnd.cpp.Fields.Float import Float64
from BackEnd.cpp.Fields.Integer import Integer
from BackEnd.cpp.Fields.EnumReference import EnumReference
from BackEnd.cpp.Fields.Flag import Flag
from BackEnd.cpp.Fields.Collection import Collection

from Model.Types.Integer import Integer as ModelInt
from Model.Types.Float import Float as ModelFloat
from Model.Types.Reference import Reference as ModelReference
from Model.Enumeration import Enumeration as ModelEnum
from Model.Types.Flag import Flag as ModelFlag
from Model.Collection import Collection as ModelCollection
from Model.Field import Field as ModelField

def create(type_name, field, endianness, settings):
    if type(field.type()) is ModelInt:
        return Integer(type_name,field, endianness, settings)
    elif type(field.type()) is ModelFloat:
        if field.size_in_bits() == 32:
            return Float32(type_name, field, endianness)
        else:
            assert field.size_in_bits() == 64, "unknown size for float type: {}".format(field.size_in_bits)
            return Float64(type_name, field, endianness)
    elif type(field.type()) is ModelReference:
        if type(field.type().referenced_type()) is ModelEnum:
            return EnumReference(type_name, field, endianness, settings)
        else:
            assert False, "Unsupported tield type"
    elif type(field.type()) is ModelFlag:
        return Flag(type_name, field, endianness, settings)
    elif type(field.type()) is ModelCollection:
        # This is very dodgy. We create a fake new field based on the type of the collection
        # The only reason we do that is so we can translate it to a cpp field so we can query it for it's cpp type
        fakeField = ModelField("", field.type().type(), 0, None, None)
        fakeField = create("", fakeField, endianness, settings)
        return Collection(type_name, field, fakeField.cpp_type(), endianness)
    else:
        assert False, "Unknown type {} and length {}".format(field.type(), field.size_in_bits())