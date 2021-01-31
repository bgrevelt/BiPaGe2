import unittest
import tostring_integrationtest
import namespace_integrationtest
import non_standard_size_big_endian_integrationtest
import non_standard_size_input_validation_integrationtest
import non_standard_size_integrationtest
import non_standard_size_misaligned_standard_type_integrationtest
import reserved_integrationtest
import simple_big_endian_integrationtest
import simple_integrationtest

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(tostring_integrationtest.ToString))
    test_suite.addTest(unittest.makeSuite(namespace_integrationtest.Namespace))
    test_suite.addTest(unittest.makeSuite(non_standard_size_big_endian_integrationtest.NonStandardSizeBigEndian))
    test_suite.addTest(unittest.makeSuite(non_standard_size_input_validation_integrationtest.NonStandardSizeInputValidation))
    test_suite.addTest(unittest.makeSuite(non_standard_size_integrationtest.NonStandardSize))
    test_suite.addTest(unittest.makeSuite(non_standard_size_misaligned_standard_type_integrationtest.NonStandardSizeMisalignedStandardType))
    test_suite.addTest(unittest.makeSuite(simple_big_endian_integrationtest.SimpleBigEndian))
    test_suite.addTest(unittest.makeSuite(reserved_integrationtest.Reserved))
    test_suite.addTest(unittest.makeSuite(simple_integrationtest.Simple))

    return test_suite

mySuit=suite()

runner=unittest.TextTestRunner()
runner.run(mySuit)