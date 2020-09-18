import sys
from antlr4 import *
from generated.BiPaGeLexer import BiPaGeLexer
from generated.BiPaGeParser import BiPaGeParser
from Model.Builder import Builder
import argparse
from compiler.BackEnd.cpp.Generator import Generator as CppGen

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', dest='input', action='append', type=str, required=True, help='input file')
    parser.add_argument('-o', dest='output', action='store', type=str, required=True, help='Directory to writ the output files')

    return parser.parse_args()

def main(argv):
    args = parse_arguments()
    codegen = CppGen(args.output)

    for file in args.input:
        input_stream = FileStream(file)
        lexer = BiPaGeLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = BiPaGeParser(stream)
        tree = parser.definition()
        walker = ParseTreeWalker()
        modelbuilder = Builder()
        walker.walk(modelbuilder, tree)
        model = modelbuilder.model()

        codegen.Generate(model)

if __name__ == '__main__':
    main(sys.argv)