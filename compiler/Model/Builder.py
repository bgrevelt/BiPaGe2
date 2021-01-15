from generated.BiPaGeListener import BiPaGeListener
from .DataType import DataType
from .Field import Field
from .Definition import Definition
from .CaptureScope import CaptureScope
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
        self._scoped_offset = 0
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

    def get_fields_from_scoped_capture_scope(self, capture_scope):
        return [self.noderesult[field] for field in capture_scope.simple_field() if self.noderesult[field].name is not None]

    def exitDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        fields = []
        ''' We get a little dodgy with the mode here. Our model looks like this
        DataType
        +-Fields
        +-Capture Scope
          +-Fields
          
        However, because we really only use the capture scope to determine offsets and capture width
        for the fields it encompasses (and some semantic analysis). After that, the extra nesting only
        makes our life harder. That's why we add all fields (including those in capture scopes) directly
        to the datatype. We still create a capture type and put the fields inside the capture type to it,
        but that's only used for semantic analysis.
        '''

        for field in ctx.field():
            if field.simple_field() and self.noderesult[field.simple_field()].name is not None:
                fields.append(self.noderesult[field.simple_field()])
            elif field.capture_scope():
                # Add fields from the capture scope directly to the datatype as well.
                fields.extend(self.get_fields_from_scoped_capture_scope(field.capture_scope()))

        capture_scopes = [ self.noderesult[cs_context.capture_scope()] for cs_context in ctx.field() if cs_context.capture_scope()]

        node = DataType(str(ctx.Identifier()), capture_scopes, fields, ctx.start)
        self.noderesult[ctx] = node

    def exitSimple_field(self, ctx:BiPaGeParser.Simple_fieldContext):
        id = str(ctx.Identifier()) if ctx.Identifier() is not None else None
        type = self.remove_aliases(str(ctx.Type()))
        field = Field(id, type, self._offset, ctx.start)
        self._offset += field.size_in_bits
        self.noderesult[ctx] = field

    def enterCapture_scope(self, ctx:BiPaGeParser.Capture_scopeContext):
        # store the current offset as that is the offset of the capture scope
        self._scoped_offset = self._offset

    def exitCapture_scope(self, ctx:BiPaGeParser.Capture_scopeContext):
        fields = [self.noderesult[field] for field in ctx.simple_field()]
        capture_scope_size = sum(f.size_in_bits for f in fields)
        capture_scope_offset = self._scoped_offset

        for field in ctx.simple_field():
            self.noderesult[field].set_capture(capture_scope_size, capture_scope_offset)

        self.noderesult[ctx] = CaptureScope(capture_scope_offset, fields, ctx.start)

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

    def is_aliased_type(self, type):
        return re.search("^[s,u,f]\d{1,2}$",type) is not None

    def remove_aliases(self, type):
        if self.is_aliased_type(type):
            return self.fieldtype_translation[type[0]] + type[1:]
        else:
            return type

