from generated.BiPaGeParser import BiPaGeParser
from generated.BiPaGeListener import BiPaGeListener
from .DataType import DataType
from .Field import Field

class Builder(BiPaGeListener):
    def __init__(self):
        self._offset = 0
        self.elements = []
        self.noderesult = {}

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

    def enterDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        self._offset = 0

    def exitDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        node = DataType(str(ctx.Identifier()), [self.noderesult[field] for field in ctx.field()])
        self.elements.append(node)

    def exitField(self, ctx:BiPaGeParser.FieldContext):
        id = str(ctx.Identifier())
        type = self.remove_aliases(str(ctx.Type()))
        field = Field(id, type, self._offset)
        self._offset += field.size()
        self.noderesult[ctx] = field


    def model(self):
        return self.elements

    def remove_aliases(self, type):
        if type in self.fieldtype_translation:
            return self.fieldtype_translation[type]
        else:
            return type