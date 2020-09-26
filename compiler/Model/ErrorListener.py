from antlr4.error.ErrorListener import ErrorListener
from .BuildMessage import BuildMessage

class BiPaGeErrorListener(ErrorListener):
    def __init__(self):
        self._errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self._errors.append(BuildMessage(line, column, msg))

    def errors(self):
        return self._errors