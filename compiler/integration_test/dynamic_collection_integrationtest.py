import unittest
from integration_test.integrationtest import IntegrationTest

class Collection(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        Foo
        {
            field1: s32;
            field2: s16[field1];
            field3: u16;
            field4: u8[field3];
            field5: f64;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "dynamic_collection_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int32_t>(8));
    
    std::vector<std::int16_t> field2_values {
        6886,
        32559,
        -26790,
        9919,
        3793,
        -9843,
        -3452,
        26278
    };
        
    for(size_t i=0 ; i<field2_values.size() ; ++i)
        p = serialize(p, field2_values[i]);
        
    p = serialize(p, static_cast<std::uint16_t>(5));
     
    std::vector<std::uint8_t> field4_values {
        0,
        77,
        109,
        234,
        255   
    };
        
    for(size_t i=0 ; i<field4_values.size() ; ++i)
        p = serialize(p, field4_values[i]);
    
    p = serialize(p, 1.234);

    Foo_view parsed(buffer);

    check_equal(parsed.field1(), 8);
    auto collection = parsed.field2();
    check_equal(collection.size(), field2_values.size());
    for(size_t i = 0 ; i < collection.size() ; ++i)
    {
        check_equal(collection[i], field2_values[i]);
    }
    check_equal(parsed.field3(), 5);
    auto collection2 = parsed.field4();
    check_equal(collection2.size(), field4_values.size());
    for(size_t i = 0 ; i < collection2.size() ; ++i)
    {
        check_equal(collection2[i], field4_values[i]);
    }
    check_equal(parsed.field5(), 1.234);
}


void test_foo_builder()
{
    int32_t field1 = 12;
    std::vector<std::int16_t> field2 {
        6886,
        32559,
        -26790,
        9919,
        3793,
        -9843,
        -3452,
        26278,
        -30189,
        -24717,
        -534,
        -30559 
    };
    std::uint16_t field3 = 5;
    std::vector<std::uint8_t> field4 {
        0,
        77,
        109,
        234,
        255   
    };
    double field5 = 1.234;
    Foo_builder builder(field1, field2, field3, field4, field5);
    
    std::vector<uint8_t> expected(43);
    auto p = expected.data();
    p = serialize(p, static_cast<std::int32_t>(12));
    for(size_t i=0 ; i<field2.size() ; ++i)
        p = serialize(p, field2[i]);
    p = serialize(p, static_cast<std::uint16_t>(5));        
    for(size_t i=0 ; i<field4.size() ; ++i)
        p = serialize(p, field4[i]);
    p = serialize(p, 1.234);

    auto result = builder.build();
    check_equal(result, expected);
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