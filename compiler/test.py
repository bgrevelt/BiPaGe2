import sys
from antlr4 import *
from generated.BiPaGeLexer import BiPaGeLexer
from generated.BiPaGeParser import BiPaGeParser
from generated.BiPaGeListener import BiPaGeListener
from Model.Builder import Builder
from compiler.BackEnd.cpp.Generator import Generator
 
def main(argv):
    input_stream = InputStream('''
    Foo {
    field1: int32;
    field2: float64;
    field3 : uint8;
    }
    
    Bar {
    field1: int8;
    field2: float32;
    field3 : uint64;
    }
    ''')
    lexer = BiPaGeLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = BiPaGeParser(stream)
    tree = parser.definition()
    walker = ParseTreeWalker()
    modelbuilder = Builder()
    walker.walk(modelbuilder, tree)
    model = modelbuilder.model()
    codegen = Generator("compiler_output")
    codegen.Generate(model)

if __name__ == '__main__':
    main(sys.argv)