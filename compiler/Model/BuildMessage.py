class BuildMessage:
    def __init__(self, path, line, column, message):
        self.line = line
        self.column = column
        self.message = message
        self.path = path

    def __str__(self):
        return f'p: {self.path} l: {self.line}, c:{self.column}, m:{self.message}'

    def __repr__(self):
        return self.__str__()

class BuildMessageContainer:
    def __init__(self, path):
        self._path = path
        self._warnings = []
        self._errors = []

    def add_warning(self, message, line, column):
        self._add_message(self._warnings, message, line, column)

    def add_error(self, message, line, column):
        self._add_message(self._errors, message, line, column)

    def _add_message(self, collection, message, line, column):
        collection.append(BuildMessage(self._path, line, column, message))

    def warnings(self):
        return self._warnings

    def errors(self):
        return self._errors

    def error_count(self):
        return len(self._errors)