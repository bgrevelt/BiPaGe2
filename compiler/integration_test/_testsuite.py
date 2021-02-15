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

    return test_suite

mySuit=suite()

runner=unittest.TextTestRunner()
runner.run(mySuit)