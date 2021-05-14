from Model.Expressions.Expression import Expression

class TernaryOperator(Expression):
    def __init__(self, condition, true, false, token=None):
        super().__init__(token)
        self._condition = condition
        self._true = true
        self._false = false

    def evaluate(self):
        evaluated_condition = self._condition.evaluate()
        evaluated_true = self._true.evaluate()
        evaluated_false = self._false.evaluate()

        assert type(evaluated_condition) is bool, f"Condition operand must resolve to boolean type, not {type(evaluated_condition)}"

        return evaluated_true if evaluated_condition else evaluated_false

    def Equals(self, other):
        return type(other) is TernaryOperator and \
            self._condition.Equals(other._condition) and \
            self._true.Equals(other._true) and \
            self._false.Equals(other._false)

    def __str__(self):
        return f'{str(self._condition)} ? {str(self._true)} : {str(self._false)}'

