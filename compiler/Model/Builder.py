from generated.BiPaGeListener import BiPaGeListener
from .DataType import DataType
from .Field import Field
from .Definition import Definition
from .ErrorListener import BiPaGeErrorListener
from antlr4 import *
from generated.BiPaGeLexer import BiPaGeLexer
from generated.BiPaGeParser import BiPaGeParser
import re


def set_error_listener(target, listener):
    target.removeErrorListeners()
    target.addErrorListener(listener)


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
            if field.simple_field():
                field = field.simple_field()
            elif field.divided_field():
                field = field.divided_field()

            if self.noderesult[field].name is not None: # if no name is set, this is a padding field and we can ignore it.
                fields.append(self.noderesult[field])

        node = DataType(str(ctx.Identifier()), fields, ctx.start)
        self.noderesult[ctx] = node

    def exitSimple_field(self, ctx:BiPaGeParser.Simple_fieldContext):
        id = str(ctx.Identifier()) if ctx.Identifier() is not None else None
        type = self.remove_aliases(str(ctx.Type()))
        field = Field(id, type, self._offset, ctx.start)
        self._offset += field.size_in_bits
        self.noderesult[ctx] = field

    def exitScoped_field(self, ctx:BiPaGeParser.Scoped_fieldContext):
        raise NotImplementedError("exitDivided_field not implemented in lister yet")

    def build(self, text):
        errors = []
        warnings = []
        model = None
        errorlistener = BiPaGeErrorListener()
        lexer = BiPaGeLexer(InputStream(text))
        set_error_listener(lexer, errorlistener)

        parser = BiPaGeParser(CommonTokenStream(lexer))
        set_error_listener(parser, errorlistener)
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