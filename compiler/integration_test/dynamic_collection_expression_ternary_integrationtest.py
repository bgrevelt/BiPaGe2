import unittest
from integration_test.integrationtest import IntegrationTest

class DynamicCollectionExpressionTernary(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''        
        Foo
        {
            {
                flag1:flag;
                flag2:flag;
                u6;   
            }
            collection1: u8[flag1?10:0];
            collection2: u8[flag2?10:0];     
            field1: f64;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "dynamic_collection_expression_ternary_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    
    std::vector<std::uint8_t> collection1_values { 1,2,3,4,5,6,7,8,9,10 };
    std::vector<std::uint8_t> collection2_values { }; // empty collection
    
    p = serialize(p, static_cast<std::uint8_t>(1)); // flag1 set, flag2 clear
    p = serialize(p, collection1_values);
    p = serialize(p, collection2_values);
    p = serialize(p, 1.234);

    Foo_view parsed(buffer);

    check_equal(parsed.flag1(), true);
    check_equal(parsed.collection1(), collection1_values);
    check_equal(parsed.collection2(), collection2_values);
    check_equal(parsed.field1(), 1.234);
    check_equal(parsed.size(), 19);
}

int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "view") == 0)
        test_foo_view();
}''')

    def test_foo_view(self):
        exit_code, output = self.run_all(testargs=["view"])
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()