from generated.BiPaGeParser import BiPaGeParser
from generated.BiPaGeListener import BiPaGeListener
from .DataType import DataType
from .Field import Field

class Builder(BiPaGeListener):
    def __init__(self):
        self._offset = 0
        self.elements = []

        # remove the type aliases here so we don't have to worry about it in the backend.
        self.fieldtype_translation = {
            'u8': 'uint8',
            's8': 'int8',
            'u16': 'uint16',
            's16': 'int16',
            'u32': 'uint32',
            's32': 'int32',
            'f32': 'float32',
            'f64': 'float64',
        }

    def enterField(self, ctx:BiPaGeParser.FieldContext):
        field = Field(str(ctx.Identifier()), self.remove_aliases(str(ctx.Type())), self._offset)
        self.elements[-1].add_field(field)
        self._offset += field.size()

    def enterDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        self._offset = 0
        self.elements.append(DataType(str(ctx.Identifier())))

    def model(self):
        return self.elements

    def remove_aliases(self, type):
        if type in self.fieldtype_translation:
            return self.fieldtype_translation[type]
        else:
            return type