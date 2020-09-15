import sys
from antlr4 import *
from generated.BiPaGeLexer import BiPaGeLexer
from generated.BiPaGeParser import BiPaGeParser
from generated.BiPaGeListener import BiPaGeListener

class Element:
    def __init__(self, identifier):
        self.fields = []
        self.identifier = str(identifier)

    def add_field(self,field):
        self.fields.append(field)

    def __str__(self):
        s = self.identifier + "\n"
        for field in self.fields:
            s += f"\t{field.name} : {field.type}\n"
        return s

class Field:
    def __init__(self, name, type):
        self.name = str(name)
        self.type = str(type)

class Test(BiPaGeListener):
    def enterField(self, ctx:BiPaGeParser.FieldContext):
        elements[-1].add_field(Field(ctx.Identifier(), ctx.Type()))

    def enterElement(self, ctx:BiPaGeParser.ElementContext):
        elements.append(Element(ctx.Identifier()))

    def exitElements(self, ctx):
        for element in elements:
            print(element)


elements = []
 
def main(argv):
    input_stream = FileStream("../grammar/input.txt")
    lexer = BiPaGeLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = BiPaGeParser(stream)
    tree = parser.elements()
    walker = ParseTreeWalker()
    walker.walk(Test(), tree)
 
if __name__ == '__main__':
    main(sys.argv)