from generated.BiPaGeParser import BiPaGeParser
from generated.BiPaGeListener import BiPaGeListener
from .DataType import DataType
from .Field import Field

class Builder(BiPaGeListener):
    def __init__(self):
        self._offset = 0
        self.elements = []

    def enterField(self, ctx:BiPaGeParser.FieldContext):
        field = Field(str(ctx.Identifier()), str(ctx.Type()), self._offset)
        self.elements[-1].add_field(field)
        self._offset += field.size()

    def enterDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        self._offset = 0
        self.elements.append(DataType(str(ctx.Identifier())))

    def model(self):
        return self.elements