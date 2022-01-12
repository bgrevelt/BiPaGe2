from Model.Expressions.Expression import Expression
from Model.types import SignedInteger, UnsignedInteger, Flag
from Model.Expressions.NumberLiteral import NumberLiteral

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

        if type(evaluated_condition) is bool:
            # if the condition can be 'compile time' evaluated to a boolean, we can evaluate the operator to just the
            # evaluated true or false clause
            return evaluated_true if evaluated_condition else evaluated_false
        else:
            # if not, we can't 'evaluate away' the ternary operator itself, but maybe we can simplify the clauses
            self._true = evaluated_true
            self._false = evaluated_false
            return self

    def Equals(self, other):
        return type(other) is TernaryOperator and \
            self._condition.Equals(other._condition) and \
            self._true.Equals(other._true) and \
            self._false.Equals(other._false)

    def check_semantics(self, warnings, errors):
        self._condition.check_semantics(warnings, errors)
        self._true.check_semantics(warnings, errors)
        self._false.check_semantics(warnings, errors)
        return_type_true = self._true.return_type()
        return_type_false = self._false.return_type()
        return_type_condition = self._condition.return_type()

        if return_type_condition not in [bool, Flag]:
            self.add_message(
                f'{return_type_condition.__name__} not allowed as ternary condition',
                errors)

        # We can mix and match signed integers, unsigned integers, and number literals
        allowed_mix = return_type_true in [SignedInteger, UnsignedInteger, NumberLiteral] \
                      and return_type_false in [SignedInteger, UnsignedInteger, NumberLiteral]

        if not allowed_mix and return_type_true != return_type_false:
            self.add_message(
                f'Different types for true ({return_type_true.__name__}) and false ({return_type_false.__name__}) clause',
                errors
            )

    def return_type(self):
        return_type_true = self._true.return_type()
        return_type_false = self._false.return_type()
        if return_type_true == SignedInteger or return_type_false == SignedInteger:
            return SignedInteger
        else:
            assert return_type_true == return_type_false, f'True and false clause have different return types ({return_type_true} and {return_type_false})'
            return return_type_true

    def __str__(self):
        return f'{str(self._condition)} ? {str(self._true)} : {str(self._false)}'

