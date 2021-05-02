from Model.Expressions.Expression import Expression
from Model.Node import Node

class NumberLiteral(Expression):
    def __init__(self, number, token=None):
        super().__init__(token)
        self._number = number

    def evaluate(self):
        return self._number

    def Equals(self, other):
        return type(other) is NumberLiteral and other._number == self._number

    def __str__(self):
        return str(self._number)