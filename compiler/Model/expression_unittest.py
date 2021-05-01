import unittest
from build_model import build_model_from_text
from Model.Collection import Collection

class ExpressionUnittests(unittest.TestCase):
    def test_simple(self):
        expression = self._build_expression('1+1^2/3*8')
        print(expression)

    #TODO: This will fail because the grammar will interpret 1-1 as two number literals: '1' and '-1'
    # Simplest solution would probably to add a unary minus operator.
    def test_subtract(self):
        expression = self._build_expression('1-1')
        print(expression)

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