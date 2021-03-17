from Model.Expressions.Expression import Expression
from Model.Node import Node

class NumberLiteral(Expression):
    def __init__(self, number, token):
        super().__init__(token)
        self._number = number

    def evaluate(self):
        return self._number