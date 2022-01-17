import unittest
from integration_test.integrationtest import IntegrationTest

class NestedDataType(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        Foo
        {
            field1: s32;
            f32;
            field3: u16;
            field4: u8[field3];
            field5: f64;
        }
        Bar
        {
            f1: s32;
            f2: Foo;
            f3: f64;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "nested_data_type_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    
}


void test_foo_builder()
{
   
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "view") == 0)
        test_foo_view();
    if(strcmp(argv[1], "build") == 0)
        test_foo_builder();
}''')

    def test_foo_view(self):
        exit_code, output = self.run_all(testargs=["view"])
        self.assertEqual(exit_code, 0)

    def test_foo_builder(self):
        exit_code, output = self.run_all(testargs=["build"])
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()