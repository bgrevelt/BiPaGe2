import unittest
from compiler.integration_test.integrationtest import IntegrationTest

class DynamicCollectionExpressionMul(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''        
        Foo
        {
            field1: s32;
            field2: s16;
            collection1: u8[field1 * 5];
            collection2: u8[5 * field1];
            collection3: u8[field1 * field2];     
            collection4: u8[field2 * field1];     
            field5: f64;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "dynamic_collection_expression_mul_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    std::vector<std::uint8_t> collection1_values { 1,2,3,4,5,6,7,8,9,10 };
    std::vector<std::uint8_t> collection2_values { 11,12,13,14,15,16,17,18,19,20 };
    std::vector<std::uint8_t> collection3_values { 21,22,23,24,25,26 };
    std::vector<std::uint8_t> collection4_values { 21,22,23,24,25,26 };
    
    p = serialize(p, static_cast<std::int32_t>(2));
    p = serialize(p, static_cast<std::int16_t>(3));
    p = serialize(p, collection1_values);
    p = serialize(p, collection2_values);
    p = serialize(p, collection3_values);
    p = serialize(p, collection4_values);
    p = serialize(p, 1.234);

    Foo_view parsed(buffer);

    check_equal(parsed.field1(), 2);
    check_equal(parsed.field2(), 3);
    check_equal(parsed.collection1(), collection1_values);
    check_equal(parsed.collection2(), collection2_values);
    check_equal(parsed.collection3(), collection3_values);
    check_equal(parsed.collection4(), collection4_values);
    check_equal(parsed.field5(), 1.234);
    check_equal(parsed.size_in_bytes(), 46);
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