from generated.BiPaGeListener import BiPaGeListener
from generated.BiPaGeParser import BiPaGeParser
from .DataType import DataType
from .Field import Field
from .Definition import Definition
from .CaptureScope import CaptureScope
from compiler.Model.types import Flag
from compiler.Model.Enumeration import Enumeration
from compiler.Model.Collection import Collection
from compiler.Model.expressions import *
import os
from compiler.Model.helpers import *
from typing import List

class Builder(BiPaGeListener):
    def __init__(self, file, imports):
        self._static_offset = 0
        self._dynamic_offset = None
        self._static_capture_offset = 0
        self._dynamic_capture_offset = None
        self._definition = None
        self.noderesult = {}
        self._definition_name = os.path.splitext(os.path.split(file)[1])[0] if file is not None else 'default_name'
        self._imported_enumerations_by_name = {} # We store these separately from the local enumerations because we don't perform any analysis on these (that's done when the imported file is compiled)
        self._enumerations_by_enumerator_fully_qualified_name = {}
        self._enumerations_by_name = {}
        self._data_types_by_name = {}
        self._imports = imports
        self._imported_types_by_name = {}
        self._process_imports(imports)

        # We have this here to store fields in the current datatype as we encounter them. The reason that we can't
        # use noderesult like we do with everything else is that we want to have all fields that are in a datatype
        # included those that are in a capture scope directly in the datatype. If we used the 'normal' approach, we
        # could still add all the fields in all capture scopes directly to the datatype, but we'd lose the ordering information
        # For example, Foo{ f1 : u8; { f2: u4; f3:u4; } f3:s32;} would give us two fields and a capture scope, but we w
        # would need to resort to hacky tricks to find out in which order they were defined. This doesn't really matter
        # because the generated code would still be valid, but it's nicer if the getters/setters in the generated code
        # have the same order as in the input file. So we use this approach to do just that.
        self._current_datatype_fields = []


    def _process_imports(self, imports:List[Definition]):
        for definition in imports:
            ns = definition.namespace_as_string()
            for enum in definition.enumerations:
                enumeration_name = (ns + "." if ns else "") + enum.name()
                self._imported_enumerations_by_name[enumeration_name] = enum
                for enumerator_name,_ in enum.enumerators():
                    enumerator_fully_qualified_name = f'{enumeration_name}.{enumerator_name}'
                    self._enumerations_by_enumerator_fully_qualified_name[enumerator_fully_qualified_name] = enum
            for dt in definition.datatypes:
                data_type_name = (ns + "." if ns else "") + dt.identifier
                self._data_types_by_name[data_type_name] = dt


    def exitDefinition(self, ctx:BiPaGeParser.DefinitionContext):
        namespace = []
        if ctx.namespace():
            namespace = [str(ns) for ns in ctx.namespace().Identifier()]

        if ctx.endianness():
            assert str(ctx.endianness().EndiannessDecorator()) in ['@bigendian','@littleendian']
        endianness = 'little'
        if ctx.endianness() and str(ctx.endianness().EndiannessDecorator()) == '@bigendian':
            endianness = 'big'

        datatypes = [self.noderesult[d] for d in ctx.datatype()]
        enumerations = self._enumerations_by_name.values()
        self._definition = Definition(self._definition_name, endianness, namespace, self._imports, datatypes, enumerations, ctx.start)


    def enterDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        self._static_offset = 0
        self._dynamic_offset = None
        self._static_capture_offset = 0
        self._dynamic_capture_offset = None

    def exitDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        capture_scopes = [self.noderesult[capture_scope] for capture_scope in ctx.capture_scope()]

        node = DataType(str(ctx.Identifier()), capture_scopes, self._current_datatype_fields, ctx.start)
        self.noderesult[ctx] = node
        self._data_types_by_name[node.identifier] = node

        self._current_datatype_fields = []

    def exitField(self, ctx:BiPaGeParser.FieldContext):
        id = str(ctx.Identifier()) if ctx.Identifier() is not None else None
        field_type = self.noderesult[ctx.field_type()]

        if type(field_type) is Enumeration and field_type.name() == "":
            # This is an inline enumeration. By definition it doesn't have a name. We use the name of the field to name
            # the enumeration
            name = f'{id}_ENUM' if id is not None else None
            enum = field_type
            enum.setname(name)
            self._enumerations_by_name[name] = enum

            # Create a reference. This way our model doesn't have to know about the difference between a normal enum
            # and an inline enumeration. Just like with a normal enum, we create an enum definition (using the field
            # name to generate a name for the enum) and we refer to that type by name in the field.
            reference = EnumerationReference(name, enum, ctx.start)
            self.noderesult[ctx.field_type()] = reference
            field_type = reference

        if ctx.multiplier():
            # this is a collection
            field_type = Collection(field_type, self.noderesult[ctx.multiplier()],ctx.start)

        field = Field(id, field_type, self._static_offset, self._dynamic_offset, ctx.start)

        size = field.size_in_bits()
        if size is None:
            # This field has a dynamic size. This will be the dynamic offset for the next field
            self._dynamic_offset = field
            self._static_offset = 0
        else:
            # This field has a static size
            self._static_offset += field.size_in_bits()

        self.noderesult[ctx] = field
        self._current_datatype_fields.append(field)

    def enterCapture_scope(self, ctx:BiPaGeParser.Capture_scopeContext):
        # store the current offset as that is the offset of the capture scope
        self._static_capture_offset = self._static_offset
        self._dynamic_capture_offset = self._dynamic_offset

    def exitCapture_scope(self, ctx:BiPaGeParser.Capture_scopeContext):
        fields = [self.noderesult[field] for field in ctx.field()]
        capture_scope_size = sum(f.size_in_bits() for f in fields)

        for field in ctx.field():
            self.noderesult[field].set_capture(capture_scope_size, self._static_capture_offset, self._dynamic_capture_offset)

        self.noderesult[ctx] = CaptureScope(self._static_capture_offset, fields, ctx.start)

    def exitField_type(self, ctx:BiPaGeParser.Field_typeContext):
        if ctx.IntegerType():
            type, size = split_sized_type(remove_aliases(str(ctx.IntegerType())))
            signed = type == 'int'
            self.noderesult[ctx] = SignedInteger(size, ctx.start) if signed else UnsignedInteger(size, ctx.start)
        elif ctx.FloatingPointType():
            _, size = split_sized_type(str(ctx.FloatingPointType()))
            self.noderesult[ctx] = Float(size, ctx.start)
        elif ctx.reference():
            self.noderesult[ctx] = self.noderesult[ctx.reference()]
        elif ctx.FlagType():
            self.noderesult[ctx] = Flag(ctx.start)
        elif ctx.inline_enumeration():
            self.noderesult[ctx] = self.noderesult[ctx.inline_enumeration()]

    def _find_field(self, name):
        return next((field for field in self._current_datatype_fields if name == field.name), None)

    def exitReference(self, ctx:BiPaGeParser.ReferenceContext):
        name = ".".join(str(id) for id in ctx.Identifier())
        if name in self._enumerations_by_name:
            self.noderesult[ctx] = EnumerationReference(name, self._enumerations_by_name[name], ctx.start)
        elif name in self._imported_enumerations_by_name:
            self.noderesult[ctx] = EnumerationReference(name, self._imported_enumerations_by_name[name], ctx.start)
        elif self._find_field(name):
            self.noderesult[ctx] = FieldReference(name, self._find_field(name), ctx.start)
        elif name in self._enumerations_by_enumerator_fully_qualified_name:
            self.noderesult[ctx] = EnumeratorReference(name.split('.')[-1], self._enumerations_by_enumerator_fully_qualified_name[name], ctx.start)
        elif name in self._data_types_by_name:
            self.noderesult[ctx] = DataTypeReference(name, self._data_types_by_name[name], ctx.start)
        else:
            self.noderesult[ctx] = NullReference(name, ctx.start)

    def exitEnumerand(self, ctx:BiPaGeParser.EnumerandContext):
        name = str(ctx.Identifier())
        expression = self.noderesult[ctx.expression()]

        self.noderesult[ctx] = (name, expression)

    def exitEnumeration(self, ctx:BiPaGeParser.EnumerationContext):
        type, size = split_sized_type(remove_aliases(str(ctx.IntegerType())))
        signed = type == 'int'

        type = SignedInteger(size, ctx.start) if signed else UnsignedInteger(size, ctx.start)

        name = str(ctx.Identifier())
        enumerands = [self.noderesult[e] for e in ctx.enumerand()]

        enum = Enumeration(name, type, enumerands, ctx.start)
        self.noderesult[ctx] = enum
        self._enumerations_by_name[name] = enum
        for enumerand_name, _ in enumerands:
            self._enumerations_by_enumerator_fully_qualified_name[f'{name}.{enumerand_name}'] = enum

    def exitInline_enumeration(self, ctx:BiPaGeParser.Inline_enumerationContext):
        type, size = split_sized_type(remove_aliases(str(ctx.IntegerType())))
        signed = type == 'int'
        type = SignedInteger(size, ctx.start) if signed else UnsignedInteger(size, ctx.start)
        enumerands = [self.noderesult[e] for e in ctx.enumerand()]
        enum = Enumeration("", type, enumerands, ctx.start)
        self.noderesult[ctx] = enum

    def exitImport_rule(self, ctx:BiPaGeParser.Import_ruleContext):
        self.noderesult[ctx] = str(ctx.FilePath())

    def exitMultiplier(self, ctx:BiPaGeParser.MultiplierContext):
        assert ctx.expression()
        self.noderesult[ctx] = self.noderesult[ctx.expression()]

    def exitRef(self, ctx:BiPaGeParser.RefContext):
        self.noderesult[ctx] = self.noderesult[ctx.reference()]

    def exitNumber(self, ctx:BiPaGeParser.NumberContext):
        self.noderesult[ctx] = NumberLiteral(int(str(ctx.NumberLiteral())), ctx.start)

    def exitAddSub(self, ctx:BiPaGeParser.AddSubContext):
        self._handle_binary_operator(ctx, {'+':AddOperator, '-':SubtractOperator})

    def exitMultDiv(self, ctx:BiPaGeParser.MultDivContext):
        self._handle_binary_operator(ctx, {'*': MultiplyOperator, '/': DivisionOperator})

    def exitEquality(self, ctx:BiPaGeParser.EqualityContext):
        self._handle_binary_operator(ctx, {'==': EqualsOperator, '!=': NotEqualsOperator})

    def exitRelational(self, ctx:BiPaGeParser.RelationalContext):
        self._handle_binary_operator(ctx,
                                     {'<': LessThanOperator,
                                      '<=': LessThanEqualOperator,
                                      '>': GreaterThanOperator,
                                      '>=': GreaterThanEqualOperator})

    def exitParens(self, ctx:BiPaGeParser.ParensContext):
        # precedence set by parentheses is handled by the parser, so we can omit it from the model
        # simply store the expression within the parentheses
        self.noderesult[ctx] = self.noderesult[ctx.expression()]

    def exitTernary(self, ctx:BiPaGeParser.TernaryContext):
        condition = self.noderesult[ctx.expression(0)]
        true = self.noderesult[ctx.expression(1)]
        false = self.noderesult[ctx.expression(2)]
        self.noderesult[ctx] = TernaryOperator(condition, true, false, ctx.start)

    def exitMinus(self, ctx:BiPaGeParser.MinusContext):
        n = int(str(ctx.NumberLiteral()))
        self.noderesult[ctx] = NumberLiteral(-1*n, ctx.start)


    def model(self):
        return self._definition


    def _handle_binary_operator(self, ctx, options:dict):
        assert ctx.op.text in options.keys() , f'Unexpected operator token {ctx.op.text}'
        left = self.noderesult[ctx.expression(0)]
        right = self.noderesult[ctx.expression(1)]
        self.noderesult[ctx] = options[ctx.op.text](left, right, ctx.start)

