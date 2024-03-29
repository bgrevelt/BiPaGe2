from BackEnd.cpp.Fields.Float import Float32
from BackEnd.cpp.Fields.Float import Float64
from BackEnd.cpp.Fields.Integer import Integer
from BackEnd.cpp.Fields.EnumReference import EnumReference
from BackEnd.cpp.Fields.Flag import Flag
from BackEnd.cpp.Fields.Collection import Collection, DataTypeCollection
from BackEnd.cpp.Fields.DataTypeReference import DataTypeReference

from compiler.Model.types import Integer as ModelInt, Float as ModelFloat, Flag as ModelFlag
from compiler.Model.expressions import FieldReference as ModelFieldReference, EnumerationReference as ModelEnumRef, DataTypeReference as ModelDataTypeRef
from compiler.Model.Enumeration import Enumeration as ModelEnum
from compiler.Model.Collection import Collection as ModelCollection
from compiler.Model.Field import Field as ModelField

def create(type_name, field, endianness, settings):
    if isinstance(field.type(), ModelInt):
        return Integer(type_name,field, endianness, settings)
    elif type(field.type()) is ModelFloat:
        if field.size_in_bits() == 32:
            return Float32(type_name, field, endianness)
        else:
            assert field.size_in_bits() == 64, "unknown size for float type: {}".format(field.size_in_bits)
            return Float64(type_name, field, endianness)
    elif type(field.type()) is ModelEnumRef:
        return EnumReference(type_name, field, endianness, settings)
    elif type(field.type()) is ModelFieldReference:
        if type(field.type().referenced_type()) is not ModelEnum:
            assert False, "Unsupported field type"
    elif type(field.type()) is ModelFlag:
        return Flag(type_name, field, endianness, settings)
    elif type(field.type()) is ModelCollection:
        # This is very dodgy. We create a fake new field based on the type of the collection
        # The only reason we do that is so we can translate it to a cpp field so we can query it for it's cpp type
        fakeField = ModelField("", field.type().type(), 0, None, None)
        fakeField = create("", fakeField, endianness, settings)
        if type(field.type().type()) is ModelDataTypeRef:
            return DataTypeCollection(type_name, field, fakeField.cpp_type(), endianness)
        else:
            return Collection(type_name, field, fakeField.cpp_type(), endianness)
    elif type(field.type()) is ModelDataTypeRef:
        return DataTypeReference(type_name, field,endianness, settings)
    else:
        assert False, "Unknown type {} and length {}".format(field.type(), field.size_in_bits())