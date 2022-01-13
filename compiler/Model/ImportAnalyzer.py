from generated.BiPaGeListener import BiPaGeListener
from generated.BiPaGeParser import BiPaGeParser
from Model.types import SignedInteger, UnsignedInteger
from Model.Enumeration import Enumeration
import re
from Model.ImportedFile import ImportedFile
import os
from Model.expressions import NumberLiteral
from Model.helpers import *

class ImportAnalyzer(BiPaGeListener):
    def __init__(self, path):
        self.imports = []
        self.noderesult = {}
        self.enumerations = []
        self.namespace = None
        self.path = path
        self._cwd = os.path.split(os.path.abspath(path))[0]

    def properties(self):
        return ImportedFile(self.path, self.imports, self.namespace, self.enumerations)

    def exitNamespace(self, ctx:BiPaGeParser.NamespaceContext):
        self.namespace = ".".join(str(i) for i in ctx.Identifier())

    def exitImport_rule(self, ctx:BiPaGeParser.Import_ruleContext):
        path = str(ctx.FilePath()).replace('"', '')
        if os.path.isabs(path):
            self.imports.append(path)
        else:
            self.imports.append(os.path.abspath(os.path.join(self._cwd, path)))

    def exitEnumerand(self, ctx: BiPaGeParser.EnumerandContext):
        #self.noderesult[ctx] = (str(ctx.Identifier()), int(str(ctx.NumberLiteral())))
        name = str(ctx.Identifier())
        value = ctx.value() if type(ctx.expression()) is NumberLiteral else None

        self.noderesult[ctx] = (name, value)

    def exitEnumeration(self, ctx: BiPaGeParser.EnumerationContext):
        type, size = split_sized_type(remove_aliases(str(ctx.IntegerType())))
        signed = type == 'int'
        type = type = SignedInteger(size, ctx.start) if signed else UnsignedInteger(size, ctx.start)

        name = str(ctx.Identifier())
        enumerands = [self.noderesult[e] for e in ctx.enumerand()]

        enum = Enumeration(name, type, enumerands, ctx.start)
        self.enumerations.append(enum)

