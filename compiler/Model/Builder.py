from generated.BiPaGeListener import BiPaGeListener
from generated.BiPaGeParser import BiPaGeParser

from .DataType import DataType
from .Field import Field
from .Definition import Definition
from .CaptureScope import CaptureScope

from Model.Types import Integer,Float,Reference,Flag
from Model.Enumeration import Enumeration
from Model.Collection import Collection

from Model.Expressions.NumberLiteral import NumberLiteral
from Model.Expressions.AddOperator import AddOperator
from Model.Expressions.DivisionOperator import DivisionOperator
from Model.Expressions.EqualsOperator import EqualsOperator
from Model.Expressions.GreaterThanEqualOperator import GreaterThanEqualOperator
from Model.Expressions.GreaterThanOperator import GreaterThanOperator
from Model.Expressions.LessThanEqualOperator import LessThanEqualOperator
from Model.Expressions.LessThanOperator import LessThanOperator
from Model.Expressions.MultiplyOperator import MultiplyOperator
from Model.Expressions.NotEqualsOperator import NotEqualsOperator
from Model.Expressions.PowerOperator import PowerOperator
from Model.Expressions.SubstractOperator import SubtractOperator
from Model.Expressions.TernaryOperator import TernaryOperator

import os
import re


# split a sized type (e.g int16) into the type (int) and the size(16)
def split_sized_type(type):
    typename = "".join([c for c in type if not c.isnumeric()])
    size = int("".join([c for c in type if c.isnumeric()]))
    return typename,size

def is_aliased_type(type):
    return re.search("^[s,u,f]\d{1,2}$",type) is not None

def remove_aliases(type):
    aliases = {
        'u': 'uint',
        's': 'int',
        'f': 'float'
    }
    if is_aliased_type(type):
        return aliases[type[0]] + type[1:]
    else:
        return type


class Builder(BiPaGeListener):
    def __init__(self, file, imports):
        self._static_offset = 0
        self._dynamic_offset = None
        self._static_capture_offset = 0
        self._dynamic_capture_offset = None
        self._definition = None
        self.noderesult = {}
        self._definition_name = os.path.splitext(os.path.split(file)[1])[0] if file is not None else 'default_name'
        self._imports = imports
        self._imported_enumerations_by_name = {}
        for imp in imports:
            for enum in imp.enumerations:
                name = (imp.namespace + "." if imp.namespace else "") + enum.name()
                self._imported_enumerations_by_name[name] = enum

        self._enumerations_by_name = {}

        # remove the type aliases here so we don't have to worry about it in the backend.
        self.fieldtype_translation = {
            'u' : 'uint',
            's' : 'int',
            'f' : 'float'
        }

        # We have this here to store fields in the current datatype as we encounter them. The reason that we can't
        # use noderesult like we do with everything else is that we want to have all fields that are in a datatype
        # included those that are in a capture scope directly in the datatype. If we used the 'normal' approach, we
        # could still add all the fields in all capture scopes directly to the datatype, but we'd lose the ordering information
        # For example, Foo{ f1 : u8; { f2: u4; f3:u4; } f3:s32;} would give us two fields and a capture scope, but we w
        # would need to resort to hacky tricks to find out in which order they were defined. This doesn't really matter
        # because the generated code would still be valid, but it's nicer if the getters/setters in the generated code
        # have the same order as in the input file. So we use this approach to do just that.
        self._current_datatype_fields = []

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
        imports = [self.noderesult[i] for i in ctx.import_rule()]
        self._definition = Definition(self._definition_name, endianness, namespace, imports, datatypes, enumerations, ctx.start)


    def enterDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        self._static_offset = 0

    def exitDatatype(self, ctx:BiPaGeParser.DatatypeContext):
        capture_scopes = [self.noderesult[capture_scope] for capture_scope in ctx.capture_scope()]

        node = DataType(str(ctx.Identifier()), capture_scopes, self._current_datatype_fields, ctx.start)
        self.noderesult[ctx] = node

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
            reference = Reference.Reference(name, enum, ctx.start)
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
            self.noderesult[ctx] = Integer.Integer(size,signed, ctx.start)
        elif ctx.FloatingPointType():
            _, size = split_sized_type(str(ctx.FloatingPointType()))
            self.noderesult[ctx] = Float.Float(size, ctx.start)
        elif ctx.reference():
            self.noderesult[ctx] = self.noderesult[ctx.reference()]
        elif ctx.FlagType():
            self.noderesult[ctx] = Flag.Flag(ctx.start)
        elif ctx.inline_enumeration():
            self.noderesult[ctx] = self.noderesult[ctx.inline_enumeration()]


    def exitReference(self, ctx:BiPaGeParser.ReferenceContext):
        name = ".".join(str(id) for id in ctx.Identifier())
        ref = None
        if name in self._enumerations_by_name:
            ref = self._enumerations_by_name[name]
        elif name in self._imported_enumerations_by_name:
            ref = self._imported_enumerations_by_name[name]
        else:
            for field in self._current_datatype_fields:
                if field.name == name:
                    ref = field
        self.noderesult[ctx] = Reference.Reference(name, ref, ctx.start)

    def exitEnumerand(self, ctx:BiPaGeParser.EnumerandContext):
        self.noderesult[ctx] = (str(ctx.Identifier()), int(str(ctx.NumberLiteral())))

    def exitEnumeration(self, ctx:BiPaGeParser.EnumerationContext):
        type, size = split_sized_type(remove_aliases(str(ctx.IntegerType())))
        signed = type == 'int'
        type = Integer.Integer(size,signed, ctx.start)

        name = str(ctx.Identifier())
        enumerands = [self.noderesult[e] for e in ctx.enumerand()]

        enum = Enumeration(name, type, enumerands, ctx.start)
        self.noderesult[ctx] = enum
        self._enumerations_by_name[name] = enum

    def exitInline_enumeration(self, ctx:BiPaGeParser.Inline_enumerationContext):
        type, size = split_sized_type(remove_aliases(str(ctx.IntegerType())))
        signed = type == 'int'
        type = Integer.Integer(size, signed, ctx.start)
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

    def exitPower(self, ctx:BiPaGeParser.PowerContext):
        left = self.noderesult[ctx.expression(0)]
        right = self.noderesult[ctx.expression(1)]
        self.noderesult[ctx] = PowerOperator(left, right)

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
        self.noderesult[ctx] = TernaryOperator(condition, true, false)

    def model(self):
        return self._definition


    def _handle_binary_operator(self, ctx, options:dict):
        assert ctx.op.text in options.keys() , f'Unexpected operator token {ctx.op.text}'
        left = self.noderesult[ctx.expression(0)]
        right = self.noderesult[ctx.expression(1)]
        self.noderesult[ctx] = options[ctx.op.text](left, right)

