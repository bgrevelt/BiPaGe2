from antlr4.error.ErrorListener import ErrorListener
from compiler.Model.BuildMessage import BuildMessage

class BiPaGeErrorListener(ErrorListener):
    def __init__(self, path):
        self._errors = []
        self._path = path

    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        self._errors.append(BuildMessage(self._path, line, column, msg.replace('{', '{{').replace('}','}}')))

    def errors(self):
        return self._errors