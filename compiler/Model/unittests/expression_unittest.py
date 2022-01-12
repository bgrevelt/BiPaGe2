import unittest
from build_model import build_model_from_text
from Model.Collection import Collection

from Model.expressions import *

class ExpressionUnittests(unittest.TestCase):
    def test_simple_add(self):
        expression = self._build_expression('1+12')
        expected = AddOperator(NumberLiteral(1), NumberLiteral(12))
        self.assertTrue(expression.Equals(expected))

    '''
    Let's start with a bunch of simple tests to validate the operators get created right
    Just the operator with number literals as operands
    '''
    def test_simple_subtract(self):
        expression = self._build_expression('15-12')
        expected = SubtractOperator(NumberLiteral(15), NumberLiteral(12))
        self.assertTrue(expression.Equals(expected))
        self._test_evaluate('15-12', 3)

    def test_simple_multiply(self):
        expression = self._build_expression('7*33')
        expected = MultiplyOperator(NumberLiteral(7), NumberLiteral(33))
        self.assertTrue(expression.Equals(expected))

        self._test_evaluate('7*33', 7*33)


    def test_simple_division(self):
        expression = self._build_expression('28/7')
        expected = DivisionOperator(NumberLiteral(28), NumberLiteral(7))
        self.assertTrue(expression.Equals(expected))

        self._test_evaluate('28/7', 28/7)

    def test_simple_GT(self):
        expression = self._build_expression('2>8', accept_semantic_errors=True)
        expected = GreaterThanOperator(NumberLiteral(2), NumberLiteral(8))
        self.assertTrue(expression.Equals(expected))

    def test_simple_GTE(self):
        expression = self._build_expression('8>=2', accept_semantic_errors=True)
        expected = GreaterThanEqualOperator(NumberLiteral(8), NumberLiteral(2))
        self.assertTrue(expression.Equals(expected))

    def test_simple_LT(self):
        expression = self._build_expression('5124<1', accept_semantic_errors=True)
        expected = LessThanOperator(NumberLiteral(5124), NumberLiteral(1))
        self.assertTrue(expression.Equals(expected))

    def test_simple_LTE(self):
        expression = self._build_expression('734<=3', accept_semantic_errors=True)
        expected = LessThanEqualOperator(NumberLiteral(734), NumberLiteral(3))
        self.assertTrue(expression.Equals(expected))

    def test_simple_equals(self):
        expression = self._build_expression('12==12', accept_semantic_errors=True)
        expected = EqualsOperator(NumberLiteral(12), NumberLiteral(12))
        self.assertTrue(expression.Equals(expected))

    def test_simple_not_equals(self):
        expression = self._build_expression('512!=256', accept_semantic_errors=True)
        expected = NotEqualsOperator(NumberLiteral(512), NumberLiteral(256))
        self.assertTrue(expression.Equals(expected))

    def test_simple_ternary_operator(self):
        expression = self._build_expression('5<3?25:100')
        expected = TernaryOperator(
            LessThanOperator(NumberLiteral(5),NumberLiteral(3)),
            NumberLiteral(25),
            NumberLiteral(100)
        )
        self.assertTrue(expression.Equals(expected))

    '''
    Division (and all other binary operators) is left associative
    e.g. 2/3/4 == (2/3)/4
    '''
    def test_sub_left_assoc(self):
        expression = self._build_expression('16/4/2')
        expected = DivisionOperator(DivisionOperator(NumberLiteral(16), NumberLiteral(4)), NumberLiteral(2))
        self.assertTrue(expression.Equals(expected))

    '''
    Parentheses are used to override precedence
    '''
    def test_parens(self):
        expression = self._build_expression('2*(6/3)')
        expected = MultiplyOperator(NumberLiteral(2), DivisionOperator(NumberLiteral(6), NumberLiteral(3)))
        self.assertTrue(expression.Equals(expected))

    '''
    Test operator precedence. 1+2*4/12!=35 -> (1+((2*4)/12)) != 35
    '''
    def test_operator_precedence(self):
        expression = self._build_expression('1+2*4/12!=35', accept_semantic_errors=True)
        expected = \
        NotEqualsOperator(
            AddOperator(
                NumberLiteral(1),
                DivisionOperator(
                    MultiplyOperator(
                        NumberLiteral(2),
                        NumberLiteral(4)
                    ),
                    NumberLiteral(12))
                ),
            NumberLiteral(35)
        )
        self.assertTrue(expression.Equals(expected))

    def test_evaluate_simple_add(self):
        self._test_evaluate('1+2', 3)

    def test_evaluate_simple_minus(self):
        self._test_evaluate('35-18', 17)

    def test_evaluate_simple_mult(self):
        self._test_evaluate('12*6', 72)

    def test_evaluate_simple_div(self):
        self._test_evaluate('45/9', 5)

    def test_evaluate_simple_eq(self):
        self._test_evaluate('12==12', True)
        self._test_evaluate('35==25', False)

    def test_evaluate_simple_neq(self):
        self._test_evaluate('17!=12', True)
        self._test_evaluate('12!=12', False)

    def test_evaluate_simple_lt(self):
        self._test_evaluate('5<5', False)
        self._test_evaluate('5<6', True)

    def test_evaluate_simple_lte(self):
        self._test_evaluate('5<=6', True)
        self._test_evaluate('5<=5', True)
        self._test_evaluate('5<=4', False)

    def test_evaluate_simple_gt(self):
        self._test_evaluate('5>4', True)
        self._test_evaluate('5>5', False)

    def test_evaluate_simple_gte(self):
        self._test_evaluate('5>=4', True)
        self._test_evaluate('5>=5', True)
        self._test_evaluate('5>6', False)

    def test_evaluate_complex1(self):
        self._test_evaluate('5 >= 1 ? 12 + 9 /3 : 10*2 + 5 * 5', 15)
        self._test_evaluate('5 >= 6 ? 12 + 9 /3 : 10*2 + 5 * 5', 45)

    def test_evaluate_complex2(self):
        ex = '5 == 6 ? 12 + 9 /3 : 10*some_field + 5 * 5'
        r = AddOperator(MultiplyOperator(NumberLiteral(10), NullReference('some_field', None)), NumberLiteral(25))
        self._test_evaluate(ex, r)

    def _test_evaluate(self, expression, value):
        expression = self._build_expression(expression, accept_semantic_errors=True)
        evaluated = expression.evaluate()
        if type(value) is int or type(value) is float:
            self.assertIs(type(evaluated), NumberLiteral)
            self.assertEqual(value, evaluated.value())
        elif type(value) is bool:
            self.assertIs(type(evaluated), bool)
            self.assertEqual(value, evaluated)
        elif isinstance(value, Expression):
            self.assertTrue(evaluated.Equals(value))
        else:
            assert False, "Expression evaluated to unexpected type"


    def _build_expression(self, expression_text, accept_semantic_errors=False):
        # Create a fake datatype to hold the expression. That way we can use the default entry point to build a complete
        # model
        template = \
'''Dataype
{{
    field1 : u8[{expression}];
}}'''

        warnings, errors, model = build_model_from_text(template.format(expression=expression_text), '')
        if not accept_semantic_errors:
            self.assertEqual(errors, [])
        assert len(model.datatypes) == 1
        assert len(model.datatypes[0].fields()) == 1
        assert type(model.datatypes[0].fields()[0].type()) is Collection
        return model.datatypes[0].fields()[0].type().collection_size()