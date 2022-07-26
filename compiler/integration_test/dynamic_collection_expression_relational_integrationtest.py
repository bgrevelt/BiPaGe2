import unittest
from compiler.integration_test.integrationtest import IntegrationTest

class DynamicCollectionExpressionRelational(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''        
        Foo
        {
            field1 : u32;
            collection1: u8[field1 >= 256?10:0];
            collection2: u8[field1 >= 257?9:1];
            collection3: u8[field1 >  255?8:2];
            collection4: u8[field1 >  256?7:3];    
            collection5: u8[field1 <= 256?6:4];
            collection6: u8[field1 <= 255?5:5];
            collection7: u8[field1 <  256?4:6];
            collection8: u8[field1 <  257?3:7];  
            field6: f64;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "dynamic_collection_expression_relational_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    
    std::vector<std::uint8_t> collection1_values { 1,2,3,4,5,6,7,8,9,10 };
    std::vector<std::uint8_t> collection2_values { 11}; 
    std::vector<std::uint8_t> collection3_values { 21,22,23,24,25,26,27,28};
    std::vector<std::uint8_t> collection4_values { 31,32,33};  
    std::vector<std::uint8_t> collection5_values { 41,42,43,44,45,46 };
    std::vector<std::uint8_t> collection6_values { 51,52,53,54,55};
    std::vector<std::uint8_t> collection7_values { 61,62,63,64,65,66};
    std::vector<std::uint8_t> collection8_values { 71,72,73};  
    
    p = serialize(p, static_cast<std::uint32_t>(256)); 
    p = serialize(p, collection1_values);
    p = serialize(p, collection2_values);
    p = serialize(p, collection3_values);
    p = serialize(p, collection4_values);
    p = serialize(p, collection5_values);
    p = serialize(p, collection6_values);
    p = serialize(p, collection7_values);
    p = serialize(p, collection8_values);
    p = serialize(p, 1.234);

    Foo_view parsed(buffer);

    check_equal(parsed.field1(), 256);
    check_equal(parsed.collection1(), collection1_values);
    check_equal(parsed.collection2(), collection2_values);
    check_equal(parsed.collection3(), collection3_values);
    check_equal(parsed.collection4(), collection4_values);
    check_equal(parsed.collection5(), collection5_values);
    check_equal(parsed.collection6(), collection6_values);
    check_equal(parsed.collection7(), collection7_values);
    check_equal(parsed.collection8(), collection8_values);
    check_equal(parsed.field6(), 1.234);
    check_equal(parsed.size_in_bytes(), 54);
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