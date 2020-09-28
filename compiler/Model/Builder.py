from generated.BiPaGeListener import BiPaGeListener
from .DataType import DataType
from .Field import Field
from .Definition import Definition
from .ErrorListener import BiPaGeErrorListener
from antlr4 import *
from generated.BiPaGeLexer import BiPaGeLexer
from generated.BiPaGeParser import BiPaGeParser
import re

class Builder(BiPaGeListener):
    def __init__(self):
        self._offset = 0
        self._definition = None
        self.noderesult = {}

        # remove the type aliases here so we don't have to worry about it in the backend.
        self.fieldtype_translation = {
            'u' : 'uint',
            's' : 'int',
            'f' : 'float'
        }
    def exitDefinition(self, ctx:BiPaGeParser.DefinitionContext):
        self._definition = Definition([self.noderesult[d] for d in ctx.datatype()], ctx.start)

    def enterDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        self._offset = 0

    def exitDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        fields = []
        for field in ctx.field():
            if self.noderesult[field].name is not None:
                fields.append(self.noderesult[field])
        node = DataType(str(ctx.Identifier()), fields, ctx.start)
        self.noderesult[ctx] = node

    def exitField(self, ctx:BiPaGeParser.FieldContext):
        id = str(ctx.Identifier()) if ctx.Identifier() is not None else None
        type = self.remove_aliases(str(ctx.Type()))
        field = Field(id, type, self._offset, ctx.start)
        self._offset += field.size()
        self.noderesult[ctx] = field

    def setErrorListener(self, target, listener):
        target.removeErrorListeners()
        target.addErrorListener(listener)

    def build(self, text):
        errors = []
        warnings = []
        model = None
        errorlistener = BiPaGeErrorListener()
        lexer = BiPaGeLexer(InputStream(text))
        self.setErrorListener(lexer, errorlistener)

        parser = BiPaGeParser(CommonTokenStream(lexer))
        self.setErrorListener(parser, errorlistener)
        tree = parser.definition()

        errors.extend(errorlistener.errors())
        if len(errors) == 0:
            walker = ParseTreeWalker()
            walker.walk(self, tree)
            model = self._definition
            model.check_semantics(warnings, errors)

        return warnings, errors, model

    def model(self):
        return self._definition

    def remove_aliases(self, type):
        if not re.search("^[a-zA-Z]\d+$",type):
            return type

        return self.fieldtype_translation[type[0]] + type[1:]