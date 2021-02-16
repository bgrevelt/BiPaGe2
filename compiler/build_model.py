from Model.Builder import Builder
import os
from generated.BiPaGeLexer import BiPaGeLexer
from antlr4 import *
from ErrorListener import BiPaGeErrorListener
from generated.BiPaGeParser import BiPaGeParser

def _set_error_listener(target, listener):
    target.removeErrorListeners()
    target.addErrorListener(listener)


def build_model_from_file(file):
    text = open(file).read()
    file_name = os.path.splitext(os.path.split(file)[1])[0]
    return build_model_from_text(text, file_name)


def build_model_from_text(text, filename='default_filename'):
    builder = Builder()
    builder._definition_name = filename
    errors = []
    warnings = []
    model = None

    errorlistener = BiPaGeErrorListener()
    lexer = BiPaGeLexer(InputStream(text))
    _set_error_listener(lexer, errorlistener)

    parser = BiPaGeParser(CommonTokenStream(lexer))
    _set_error_listener(parser, errorlistener)
    tree = parser.definition()

    errors.extend(errorlistener.errors())
    if len(errors) == 0:
        walker = ParseTreeWalker()
        walker.walk(builder, tree)
        model = builder.model()
        model.check_semantics(warnings, errors)

    return warnings, errors, model