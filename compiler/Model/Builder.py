from generated.BiPaGeParser import BiPaGeParser
from generated.BiPaGeListener import BiPaGeListener
from .DataType import DataType
from .Field import Field
from .Definition import Definition

class Builder(BiPaGeListener):
    def __init__(self):
        self._offset = 0
        self._definition = None
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
    def exitDefinition(self, ctx:BiPaGeParser.DefinitionContext):
        self._definition = Definition([self.noderesult[d] for d in ctx.datatype()], ctx.start)

    def enterDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        self._offset = 0

    def exitDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        node = DataType(str(ctx.Identifier()), [self.noderesult[field] for field in ctx.field()], ctx.start)
        self.noderesult[ctx] = node

    def exitField(self, ctx:BiPaGeParser.FieldContext):
        id = str(ctx.Identifier())
        type = self.remove_aliases(str(ctx.Type()))
        field = Field(id, type, self._offset, ctx.start)
        self._offset += field.size()
        self.noderesult[ctx] = field


    def model(self):
        return self._definition

    def remove_aliases(self, type):
        if type in self.fieldtype_translation:
            return self.fieldtype_translation[type]
        else:
            return type