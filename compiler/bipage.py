import sys
import argparse
from compiler.BackEnd.cpp.Generator import Generator as CppGen
from build_model import build_model_from_file

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', dest='input', action='append', type=str, required=True, help='input file')
    parser.add_argument('-o', dest='output', action='store', type=str, required=True, help='Directory to write the output files')
    parser.add_argument('--cpp-no-validate-builder-input', dest='cpp_validate_input', default=True, action='store_false')
    parser.add_argument('--cpp-no-to-string', dest='cpp_to_string', default=True,
                        action='store_false')

    return parser.parse_args()

def print_semantic_messages(file, warnings, errors):
    for error in errors:
        msg = error.message.format(file=file)
        print(f'{file}:{error.line}:{error.column} ERROR {msg}')

    for warning in warnings:
        print(f'{file}:{warning.line}:{warning.column} WARNING {warning.message}')




def main(argv):
    args = parse_arguments()
    codegen = CppGen(args)

    for file in args.input:
        warnings, errors, model = build_model_from_file(file)

        print_semantic_messages(file, warnings, errors)
        if len(errors) > 0:
            continue

        codegen.generate(model)

if __name__ == '__main__':
    main(sys.argv)