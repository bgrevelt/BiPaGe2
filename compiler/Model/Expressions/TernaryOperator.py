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

    def check_semantics(self, warnings, errors):
        #TODO
       pass

    def return_type(self):
        return_type_true = self._true.return_type()
        return_type_false = self._false.return_type()
        assert return_type_true == return_type_false, f'True and false clause have different return types ({return_type_true} and {return_type_false})'
        return return_type_true

    def __str__(self):
        return f'{str(self._condition)} ? {str(self._true)} : {str(self._false)}'

