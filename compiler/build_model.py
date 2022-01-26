from Model.Builder import Builder
import os
from generated.BiPaGeLexer import BiPaGeLexer
from antlr4 import *
from ErrorListener import BiPaGeErrorListener
from generated.BiPaGeParser import BiPaGeParser
from Model.imports.ImportAnalyzer import get_import_tree

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

def build_model_from_file(file):
    text = open(file).read()
    return build_model_from_text(text, file)


def _build_model(text, filename, imports):
    builder = Builder(filename, imports)
    warnings = []
    model = None
    errorlistener = BiPaGeErrorListener()
    walk(text, builder, errorlistener)
    errors = errorlistener.errors()
    if len(errors) == 0:
        model = builder.model()
    return warnings, errors, model

def _get_imported_models(file):
    imported_models = {}
    total_warnings = []
    total_errors = []

    tree, errors = get_import_tree(file)
    if len(errors) > 0:
        return [], errors, None

    for file in tree.imports_in_order():
        dependencies = tree.imports_for_node(file)
        assert all(dep.path() in imported_models for dep in
                   dependencies), "We should have already processed all dependencies at this point. This error indicates a problem with the import tree code"
        warnings, errors, model = _build_model(open(file).read(), file,
                                               [imported_models[dep.path()] for dep in dependencies])
        total_warnings.extend(warnings)
        total_errors.extend(errors)
        if len(total_errors) > 0:
            break
        else:
            imported_models[file] = model

    return total_warnings, total_errors, imported_models


def build_model_from_text(text, filename=None):
    if len(filename) == 0:
        filename = None

    if filename is not None:
        filename = os.path.abspath(filename)
        warnings, errors, imported_models = _get_imported_models(filename)
        model = imported_models[filename]
    else:
        # No filename, probably a unit test. I can't do anything with imports
        warnings, errors, model = _build_model(text, filename, [])

    if len(errors) == 0:
        model.check_semantics(warnings, errors)

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
        model.check_semantics(warnings, errors)

    return warnings, errors, model
