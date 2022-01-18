import unittest
from integration_test.tostring_integrationtest import *
from integration_test.namespace_integrationtest import *
from integration_test.non_standard_size_big_endian_integrationtest import *
from integration_test.non_standard_size_input_validation_integrationtest import *
from integration_test.non_standard_size_integrationtest import *
from integration_test.non_standard_size_misaligned_standard_type_integrationtest import *
from integration_test.reserved_integrationtest import *
from integration_test.simple_big_endian_integrationtest import *
from integration_test.simple_integrationtest import *
from integration_test.simple_enum_integrationtest import *
from integration_test.non_standard_size_enum_integrationtest import *
from integration_test.inline_enum_integrationtest import *
from integration_test.enum_import_integrationtest import *
from integration_test.enum_import_namespace_integrationtest import *
from integration_test.collection_integrationtest import *
from integration_test.collection_big_endian_integrationtest import *
from integration_test.collection_enum_integrationtest import *
from integration_test.dynamic_collection_integrationtest import *
from integration_test.dynamic_collection_big_endian_integrationtest import *
from integration_test.dynamic_collection_expression_add_integrationtest import *
from integration_test.dynamic_collection_expression_div_integrationtest import *
from integration_test.dynamic_collection_expression_equality_integrationtest import *
from integration_test.dynamic_collection_expression_mul_integrationtest import *
from integration_test.dynamic_collection_expression_relational_integrationtest import *
from integration_test.dynamic_collection_expression_sub_integrationtest import *
from integration_test.dynamic_collection_expression_ternary_integrationtest import *
from integration_test.nested_data_type_integrationtest import *
from integration_test.nested_data_type_no_cpp17_integrationtest import *
from integration_test.double_nested_data_type_integrationtest import *
from integration_test.nested_data_type_big_endian_integrationtest import *

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ToString))
    test_suite.addTest(unittest.makeSuite(Namespace))
    test_suite.addTest(unittest.makeSuite(NonStandardSizeBigEndian))
    test_suite.addTest(unittest.makeSuite(NonStandardSizeInputValidation))
    test_suite.addTest(unittest.makeSuite(NonStandardSize))
    test_suite.addTest(unittest.makeSuite(NonStandardSizeMisalignedStandardType))
    test_suite.addTest(unittest.makeSuite(SimpleBigEndian))
    test_suite.addTest(unittest.makeSuite(Reserved))
    test_suite.addTest(unittest.makeSuite(Simple))
    test_suite.addTest(unittest.makeSuite(SimpleEnum))
    test_suite.addTest(unittest.makeSuite(NonStandardSizeEnum))
    test_suite.addTest(unittest.makeSuite(InlineEnum))
    test_suite.addTest(unittest.makeSuite(ImportEnum))
    test_suite.addTest(unittest.makeSuite(ImportEnumNamepace))
    test_suite.addTest(unittest.makeSuite(Collection))
    test_suite.addTest(unittest.makeSuite(CollectionBigEndian))
    test_suite.addTest(unittest.makeSuite(CollectionEnum))
    test_suite.addTest(unittest.makeSuite(DynamicCollection))
    test_suite.addTest(unittest.makeSuite(DynamicCollectionBigEndian))
    test_suite.addTest(unittest.makeSuite(DynamicCollectionExpressionAdd))
    test_suite.addTest(unittest.makeSuite(DynamicCollectionExpressionDiv))
    test_suite.addTest(unittest.makeSuite(DynamicCollectionExpressionEquality))
    test_suite.addTest(unittest.makeSuite(DynamicCollectionExpressionMul))
    test_suite.addTest(unittest.makeSuite(DynamicCollectionExpressionRelational))
    test_suite.addTest(unittest.makeSuite(DynamicCollectionExpressionSub))
    test_suite.addTest(unittest.makeSuite(DynamicCollectionExpressionTernary))
    test_suite.addTest(unittest.makeSuite(NestedDataType))
    test_suite.addTest(unittest.makeSuite(NestedDataTypeNoCpp17))
    test_suite.addTest(unittest.makeSuite(DoubleNestedDataType))
    test_suite.addTest(unittest.makeSuite(NestedDataTypeBigEndian))
    return test_suite

mySuit=suite()

runner=unittest.TextTestRunner()
runner.run(mySuit)