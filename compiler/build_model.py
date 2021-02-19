from Model.Builder import Builder
import os
from generated.BiPaGeLexer import BiPaGeLexer
from antlr4 import *
from ErrorListener import BiPaGeErrorListener
from generated.BiPaGeParser import BiPaGeParser
from Model.ImportAnalyzer import ImportAnalyzer

def _set_error_listener(target, listener):
    target.removeErrorListeners()
    target.addErrorListener(listener)

def walk(input, visitor, errorListener = None):
    lexer = BiPaGeLexer(InputStream(input))
    parser = BiPaGeParser(CommonTokenStream(lexer))
    if errorListener is not None:
        _set_error_listener(lexer, errorListener)
        _set_error_listener(parser, errorListener)
    tree = parser.definition()
    if not errorListener or len(errorListener.errors()) == 0:
        ParseTreeWalker().walk(visitor, tree)

def get_imported_types(path):
    imports = []
    analyzed_imports = set()
    to_analyze = [path]
    while len(to_analyze) > 0:
        new_imports = []
        for file in to_analyze:
            analyzer = ImportAnalyzer(file)
            walk(open(file).read(), analyzer)
            props = analyzer.properties()
            imports.append(props)
            new_imports = props.imports

            analyzed_imports.add(file)

        to_analyze = [file for file in new_imports if file not in analyzed_imports]
    return imports

def build_model_from_file(file):
    text = open(file).read()
    return build_model_from_text(text, file)


def build_model_from_text(text, filename=None):
    if len(filename) == 0:
        filename = None
    imports = get_imported_types(filename) if filename is not None else None
    builder = Builder(filename, imports)
    errors = []
    warnings = []
    model = None


    errorlistener = BiPaGeErrorListener()
    walk(text,builder,errorlistener)
    errors = errorlistener.errors()
    if len(errors) == 0:
        model = builder.model()
        model.check_semantics(imports, warnings, errors)

    return warnings, errors, model

def build_model_test(text, imports=None):
    builder = Builder("test.bp", imports)
    errors = []
    warnings = []
    model = None

    errorlistener = BiPaGeErrorListener()
    walk(text, builder, errorlistener)
    errors = errorlistener.errors()
    if len(errors) == 0:
        model = builder.model()
        model.check_semantics(imports, warnings, errors)

    return warnings, errors, model
