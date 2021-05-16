from Model.Expressions.Expression import Expression
from Model.Types.Integer import Integer

class NumberLiteral(Expression):
    def __init__(self, number, token = None):
        super().__init__(token)
        self._number = number

    def evaluate(self):
        # nothing to evaluate, we're just a number literal
        return self

    def value(self):
        return self._number

    def Equals(self, other):
        return type(other) is NumberLiteral and other._number == self._number

    def check_semantics(self, warnings, errors):
        #Nothing to check for a number literal
        pass

    def return_type(self):
        return Integer

    def __str__(self):
        return str(self._number)

