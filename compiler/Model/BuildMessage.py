class BuildMessage:
    def __init__(self, line, column, message):
        self.line = line
        self.column = column
        self.message = message

    def __str__(self):
        return f'l: {self.line}, c:{self.column}, m:{self.message}'

    def __repr__(self):
        return self.__str__()