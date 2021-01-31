import unittest
from integrationtest import IntegrationTest

class NonStandardSizeInputValidation(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)

    def test(self):
        # Normal bigage settings and writing invalid values: expect an exception
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
        self.write_test_cpp_file('''
#include "../check.hpp"
#include "Foo_generated.h"

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
    check_exception(std::runtime_error, []() { test_foo_builder(); });
    check_exception(std::runtime_error, []() { test_foo_builder2(); });
}''')
        exit_code, output = self.run_all()
        self.assertEqual(exit_code, 0)

        # Compiler setting to not generate validation code and writing invalid values: don't expect an exception
        self.clean_temp_dir()
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
        self.write_test_cpp_file('''
    #include "../check.hpp"
    #include "Foo_generated.h"

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
        test_foo_builder();
        test_foo_builder2();
    }''')
        exit_code, output = self.run_all(['--cpp-no-validate-builder-input'])
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()