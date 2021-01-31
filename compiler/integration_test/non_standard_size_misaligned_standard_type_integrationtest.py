import unittest
from integrationtest import IntegrationTest


class NonStandardSizeMisalignedStandardType(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)

    def test_simple(self):
        self.write_bipage_file('''
        Foo
        {
            {
                field1: u4;  
                field2: u16;  
                field3: u12;
            }
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "Foo_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    /*
    field1: u4;  <-- 10     0xa
    field2: u16; <-- 50000  0xC350
    field3: u12; <-- 2500   0x9C4
    
    0x9C4C350A
    */
    
    std::vector<std::uint8_t> buffer { 0x0A, 0x35, 0x4C, 0x9C };
    const Foo_view& parsed = ParseFoo(buffer.data());
    
    check_equal(parsed.field1(), 10);
    check_type(std::uint8_t, parsed.field1());
    
    check_equal(parsed.field2(), 50000);
    check_type(std::uint16_t, parsed.field2());
    
    check_equal(parsed.field3(), 2500);
    check_type(std::uint16_t, parsed.field3());
}

void test_foo_builder()
{
    std::uint8_t field1 = 10;
    std::uint16_t field2 = 50000;
    std::uint16_t field3 = 2500;
    
    Foo_builder builder(field1, field2, field3);
    
    // Check getter values and types
    check_type(std::uint8_t, builder.field1());
    check_equal(builder.field1(), field1);
    
    check_type(std::uint16_t, builder.field2());
    check_equal(builder.field2(), field2);
    
    check_type(std::uint16_t, builder.field3());
    check_equal(builder.field3(), field3);

    // Check the serialization
    std::vector<std::uint8_t> expected { 0x0A, 0x35, 0x4C, 0x9C };
    auto result = builder.build();
    check_equal(result, expected);
}

void test_foo_builder2()
{
    std::uint8_t field1 = 10;
    std::uint16_t field2 = 50000;
    std::uint16_t field3 = 2500;
    
    Foo_builder builder;
    builder.field1(field1);
    builder.field2(field2);
    builder.field3(field3);
    
    // Check getter values and types
    check_type(std::uint8_t, builder.field1());
    check_equal(builder.field1(), field1);
    
    check_type(std::uint16_t, builder.field2());
    check_equal(builder.field2(), field2);
    
    check_type(std::uint16_t, builder.field3());
    check_equal(builder.field3(), field3);

    // Check the serialization
    std::vector<std::uint8_t> expected { 0x0A, 0x35, 0x4C, 0x9C };
    auto result = builder.build();
    check_equal(result, expected);
}


int main(int argc, char* argv[])
{
    test_foo_view();
    test_foo_builder();
    test_foo_builder2();
}''')

        exit_code, output = self.run_all()
        self.assertEqual(exit_code, 0)

if __name__ == '__main__':
    unittest.main()