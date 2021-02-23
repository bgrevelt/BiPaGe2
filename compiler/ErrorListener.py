from antlr4.error.ErrorListener import ErrorListener
from Model.BuildMessage import BuildMessage

class BiPaGeErrorListener(ErrorListener):
    def __init__(self):
        self._errors = []

    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        self._errors.append(BuildMessage(line, column, msg.replace('{', '{{').replace('}','}}')))

    def errors(self):
        return self._errors