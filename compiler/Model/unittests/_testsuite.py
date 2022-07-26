from compiler.Model.unittests.builder_unittest import *
from compiler.Model.unittests.semantic_analysis_expressions_unittest import *
from compiler.Model.unittests.semantic_analysis_imports_unittests import *
from compiler.Model.unittests.semantic_analysis_unittests import *
from compiler.Model.unittests.expression_unittest import *

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(BuilderUnittests))
    test_suite.addTest(unittest.makeSuite(SemanticAnalysisExpressionsUnittests))
    test_suite.addTest(unittest.makeSuite(SemanticAnalysisImportsUnittests))
    test_suite.addTest(unittest.makeSuite(SemanticAnalysisUnittests))
    test_suite.addTest(unittest.makeSuite(ExpressionUnittests))
    return test_suite

mySuit=suite()

runner=unittest.TextTestRunner()
runner.run(mySuit)