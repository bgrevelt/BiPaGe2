class SemanticMessage:
    def __init__(self, line, column, message):
        self.line = line
        self.column = column
        self.message = message