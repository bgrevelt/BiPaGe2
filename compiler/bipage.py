import sys
from antlr4 import *
from generated.BiPaGeLexer import BiPaGeLexer
from generated.BiPaGeParser import BiPaGeParser
from Model.Builder import Builder
import argparse
from compiler.BackEnd.cpp.Generator import Generator as CppGen
from antlr4.error.ErrorListener import ErrorListener

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', dest='input', action='append', type=str, required=True, help='input file')
    parser.add_argument('-o', dest='output', action='store', type=str, required=True, help='Directory to writ the output files')

    return parser.parse_args()

class BiPaGeErrorListener(ErrorListener):
    def __init__(self, file):
        self._file = file
        self._errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self._errors.append(f"{self._file}:{line}:{column} Syntax error: {msg}")

    def errors(self):
        return self._errors

def print_semantic_messages(file, warnings, errors):
    for error in errors:
        print(f'{file}:{error.line}:{error.column} ERROR {error.message}')

    for warning in warnings:
        print(f'{file}:{warning.line}:{warning.column} WARNING {warning.message}')

def main(argv):
    args = parse_arguments()
    codegen = CppGen(args.output)

    for file in args.input:
        builder = Builder()
        warnings, errors, model = builder.build(open(file).read())

        print_semantic_messages(file, warnings, errors)
        if len(errors) > 0:
            continue

        codegen.Generate(model)

if __name__ == '__main__':
    main(sys.argv)