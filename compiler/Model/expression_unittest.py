import unittest
from build_model import build_model_from_text
from Model.Collection import Collection

from Model.Expressions.NumberLiteral import NumberLiteral
from Model.Expressions.AddOperator import AddOperator
from Model.Expressions.DivisionOperator import DivisionOperator
from Model.Expressions.EqualsOperator import EqualsOperator
from Model.Expressions.GreaterThanEqualOperator import GreaterThanEqualOperator
from Model.Expressions.GreaterThanOperator import GreaterThanOperator
from Model.Expressions.LessThanEqualOperator import LessThanEqualOperator
from Model.Expressions.LessThanOperator import LessThanOperator
from Model.Expressions.MultiplyOperator import MultiplyOperator
from Model.Expressions.NotEqualsOperator import NotEqualsOperator
from Model.Expressions.PowerOperator import PowerOperator
from Model.Expressions.SubstractOperator import SubtractOperator
from Model.Expressions.TernaryOperator import TernaryOperator

class ExpressionUnittests(unittest.TestCase):
    def test_simple_add(self):
        expression = self._build_expression('1+12')
        expected = AddOperator(NumberLiteral(1), NumberLiteral(12))
        self.assertTrue(expression.Equals(expected))

    '''
    Let's start with a bunch of simple tests to validate the operators get created right
    Just the operator with number literals as operands
    '''

    # TODO: This will fail because the grammar will interpret 1-1 as two number literals: '1' and '-1'
    # Simplest solution would probably to add a unary minus operator.
    # def test_simple_subtract(self):
    #     expression = self._build_expression('15-12')
    #     expected = SubtractOperator(NumberLiteral(15), NumberLiteral(12))
    #     self.assertTrue(expression.Equals(expected))

    def test_simple_multiply(self):
        expression = self._build_expression('7*33')
        expected = MultiplyOperator(NumberLiteral(7), NumberLiteral(33))
        self.assertTrue(expression.Equals(expected))

    def test_simple_division(self):
        expression = self._build_expression('28/7')
        expected = DivisionOperator(NumberLiteral(28), NumberLiteral(7))
        self.assertTrue(expression.Equals(expected))

    def test_simple_power(self):
        expression = self._build_expression('2^8')
        expected = PowerOperator(NumberLiteral(2), NumberLiteral(8))
        self.assertTrue(expression.Equals(expected))

    def test_simple_GT(self):
        expression = self._build_expression('2>8')
        expected = GreaterThanOperator(NumberLiteral(2), NumberLiteral(8))
        self.assertTrue(expression.Equals(expected))

    def test_simple_GTE(self):
        expression = self._build_expression('8>=2')
        expected = GreaterThanEqualOperator(NumberLiteral(8), NumberLiteral(2))
        self.assertTrue(expression.Equals(expected))

    def test_simple_LT(self):
        expression = self._build_expression('5124<1')
        expected = LessThanOperator(NumberLiteral(5124), NumberLiteral(1))
        self.assertTrue(expression.Equals(expected))

    def test_simple_LTE(self):
        expression = self._build_expression('734<=3')
        expected = LessThanEqualOperator(NumberLiteral(734), NumberLiteral(3))
        self.assertTrue(expression.Equals(expected))

    def test_simple_equals(self):
        expression = self._build_expression('12==12')
        expected = EqualsOperator(NumberLiteral(12), NumberLiteral(12))
        self.assertTrue(expression.Equals(expected))

    def test_simple_not_equals(self):
        expression = self._build_expression('512!=256')
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
    Power is right associative, e.g 2^3^4 == 2^(3^4)
    '''
    def test_power_right_assoc(self):
        expression = self._build_expression('2^3^4')
        expected = PowerOperator(NumberLiteral(2), PowerOperator(NumberLiteral(3), NumberLiteral(4)))
        self.assertTrue(expression.Equals(expected))
    '''
    Division (and all other binary operators) is left associative
    e.g. 2/3/4 == (2/3)/4
    '''
    def test_sub_left_assoc(self):
        expression = self._build_expression('2/3/4')
        expected = DivisionOperator(DivisionOperator(NumberLiteral(2), NumberLiteral(3)), NumberLiteral(4))
        self.assertTrue(expression.Equals(expected))

    '''
    Parentheses are used to override precedence
    '''
    def test_parens(self):
        expression = self._build_expression('(2^3)^4')
        expected = PowerOperator(PowerOperator(NumberLiteral(2), NumberLiteral(3)), NumberLiteral(4))
        self.assertTrue(expression.Equals(expected))

    '''
    Test operator precedence. 1+2*4^4/12!=35 -> (1+((2*(4^4))/12)) != 35
    '''
    def test_operator_precedence(self):
        expression = self._build_expression('1+2*4^4/12!=35')
        expected = \
        NotEqualsOperator(
            AddOperator(
                NumberLiteral(1),
                DivisionOperator(
                    MultiplyOperator(
                        NumberLiteral(2),
                        PowerOperator(
                            NumberLiteral(4),
                            NumberLiteral(4)
                        )),
                    NumberLiteral(12))
                ),
            NumberLiteral(35)
        )
        self.assertTrue(expression.Equals(expected))



    def _build_expression(self, expression_text):
        # Create a fake datatype to hold the expression. That way we can use the default entry point to build a complete
        # model
        template = \
'''Dataype
{{
    field1 : u8[{expression}];
}}'''

        warnings, errors, model = build_model_from_text(template.format(expression=expression_text), '')
        self.assertEqual(errors, [])
        assert len(model.datatypes) == 1
        assert len(model.datatypes[0].fields()) == 1
        assert type(model.datatypes[0].fields()[0].type()) is Collection
        return model.datatypes[0].fields()[0].type().collection_size()