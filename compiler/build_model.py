from Model.Builder import Builder
import os
from generated.BiPaGeLexer import BiPaGeLexer
from antlr4 import *
from ErrorListener import BiPaGeErrorListener
from generated.BiPaGeParser import BiPaGeParser
from Model.imports.ImportAnalyzer import get_import_tree
from Model.BuildMessage import BuildMessageContainer

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
    with open(file) as f:
        text = f.read()
        return build_model_from_text(text, file)


def _build_model(text, filename, imports):
    builder = Builder(filename, imports)
    model = None
    errorlistener = BiPaGeErrorListener(filename)
    walk(text, builder, errorlistener)
    errors = errorlistener.errors()
    if len(errors) == 0:
        model = builder.model()
    return errors, model

def _get_imported_models(file):
    imported_models = {}

    tree, errors = get_import_tree(file)
    if len(errors) > 0:
        return errors, {}

    for file in tree.imports_in_order():
        dependencies = tree.imports_for_node(file)
        assert all(dep.path() in imported_models for dep in
                   dependencies), "We should have already processed all dependencies at this point. This error indicates a problem with the import tree code"
        with open(file) as f:
            errors, model = _build_model(f.read(), file,
                                               [imported_models[dep.path()] for dep in dependencies])
            if len(errors) > 0:
                break
            else:
                imported_models[file] = model

    return errors, imported_models


def build_model_from_text(text, filename=None):
    warnings = []

    if len(filename) == 0:
        filename = None

    if filename is not None:
        filename = os.path.abspath(filename)
        errors, models = _get_imported_models(filename)
        #model = imported_models[filename]
    else:
        # No filename, probably a unit test. I can't do anything with imports
        errors, model = _build_model(text, filename, [])
        models = {filename:model}

    for path, model in models.items():
        if len(errors) == 0:
            semantic_analysis_messages = BuildMessageContainer(path)
            model.check_semantics(semantic_analysis_messages)
            warnings.extend(semantic_analysis_messages.warnings())
            errors.extend(semantic_analysis_messages.errors())

    return warnings, errors, list(models.values())

def build_model_test(text, imports=None):
    builder = Builder("test.bp", imports)
    errors = []
    warnings = []
    model = None

    errorlistener = BiPaGeErrorListener("")
    walk(text, builder, errorlistener)
    errors = errorlistener.errors()
    if len(errors) == 0:
        model = builder.model()
        semantic_analysis_messages = BuildMessageContainer("")
        model.check_semantics(semantic_analysis_messages)
        warnings = semantic_analysis_messages.warnings()
        errors = semantic_analysis_messages.errors()

    return warnings, errors, model
