import unittest
from integrationtest import IntegrationTest

class NonStandardSizeInputValidation(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
                Foo
                {
                    {
                    field1: s12;  
                    field2: u20;
                    }  
                    field3: f64;
                    {
                    field4: u2;
                    field5: s4;
                    field6: s18;  
                    field7: u24;
                    field8: s16;
                    }
                }
                ''')
        self.write_cmake_file()
        self._cpp_with_validation = '''
#include "../check.hpp"
#include "non_standard_size_input_validation_integrationtest_generated.h"

void test_foo_builder()
{
    Foo_builder builder(0, 0, 0.0, 4, 0, 0, 0, 0); // 4 doesn't fit into u2
}

void test_foo_builder2()
{
    Foo_builder builder;
    builder.field1(-2049); // Doesn't fit into int12
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "foobuilder") == 0)
        check_exception(std::runtime_error, []() { test_foo_builder(); });
    if(strcmp(argv[1], "foobuilder2") == 0)
        check_exception(std::runtime_error, []() { test_foo_builder2(); });
}'''
        self._cpp_without_validation = '''
    #include "../check.hpp"
    #include "non_standard_size_input_validation_integrationtest_generated.h"

    void test_foo_builder()
    {
        Foo_builder builder(0, 0, 0.0, 4, 0, 0, 0, 0); // 4 doesn't fit into u2
    }

    void test_foo_builder2()
    {
        Foo_builder builder;
        builder.field1(-2049); // Doesn't fit into int12
    }


    int main(int argc, char* argv[])
    {
        if(strcmp(argv[1], "foobuilder") == 0)
            test_foo_builder();
        if(strcmp(argv[1], "foobuilder2") == 0)
            test_foo_builder2();
    }'''

    def test_with_validation_builder(self):
        # Normal bigage settings and writing invalid values: expect an exception
        self.write_test_cpp_file(self._cpp_with_validation)
        exit_code, output = self.run_all(testargs=["foobuilder"])
        self.assertEqual(exit_code, 0)

    def test_with_validation_builder2(self):
        # Normal bigage settings and writing invalid values: expect an exception
        self.write_test_cpp_file(self._cpp_with_validation)
        exit_code, output = self.run_all(testargs=["foobuilder2"])
        self.assertEqual(exit_code, 0)

    def test_without_validation_builder(self):
        # Compiler setting to not generate validation code and writing invalid values: don't expect an exception
        self.write_test_cpp_file(self._cpp_without_validation)
        exit_code, output = self.run_all(bipageargs=['--cpp-no-validate-builder-input'],testargs=["foobuilder"])
        self.assertEqual(exit_code, 0)

    def test_without_validation_builder2(self):
        # Compiler setting to not generate validation code and writing invalid values: don't expect an exception
        self.write_test_cpp_file(self._cpp_without_validation)
        exit_code, output = self.run_all(bipageargs=['--cpp-no-validate-builder-input'], testargs=["foobuilder2"])
        self.assertEqual(exit_code, 0)

if __name__ == '__main__':
    unittest.main()