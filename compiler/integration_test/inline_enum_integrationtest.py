import unittest
from integration_test.integrationtest import IntegrationTest

class InlineEnum(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        Foo
        {
            {
                field1 : uint2 { aap=0, noot=1, mies=2, vis=3 };
                field2 : int6 { boom = -32, roos = 0, vis = 31};
            }
            field3: f64; 
            
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "inline_enum_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_enum_values()
{
    check_equal(static_cast<int>(field1_ENUM::aap), 0);
    check_equal(static_cast<int>(field1_ENUM::noot), 1);
    check_equal(static_cast<int>(field1_ENUM::mies), 2);
    check_equal(static_cast<int>(field1_ENUM::vis), 3);
    
    check_equal(static_cast<int>(field2_ENUM::boom), -32);    
    check_equal(static_cast<int>(field2_ENUM::roos), 0);  
    check_equal(static_cast<int>(field2_ENUM::vis), 31);  
}

void test_foo_view()
{            
    
    std::uint8_t buffer[1024];
    auto p = buffer;
    
    // mies = 2 = b'10'
    // vis = 31 = b'011111'
    // combined 01111110 -> 0x7e
    
    p = serialize(p, static_cast<std::uint8_t>(0x7e));
    p = serialize(p, 1.234);

    Foo_view parsed(buffer);

    check_equal(parsed.field1(), field1_ENUM::mies);
    check_equal(parsed.field2(), field2_ENUM::vis);
    check_equal(parsed.field3(), 1.234);
    check_equal(parsed.size_in_bytes(), 9);
    
}

void test_foo_builder()
{
    Foo_builder builder(
        field1_ENUM::mies,
        field2_ENUM::vis,
        123.456);
    
    std::vector<uint8_t> expected(9);
    auto p = expected.data();
    p = serialize(p, static_cast<std::uint8_t>(0x7e));
    p = serialize(p, 123.456);
    
    auto result = builder.build();
    check_equal(result, expected);
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "enumvalues") == 0)
        test_enum_values();
    if(strcmp(argv[1], "fooview") == 0)
        test_foo_view();
    if(strcmp(argv[1], "foobuild") == 0)
        test_foo_builder();
}''')

    def test_foo_view(self):
        exit_code, output = self.run_all(testargs=["fooview"])
        self.assertEqual(exit_code, 0)

    def test_foo_builder(self):
        exit_code, output = self.run_all(testargs=["foobuild"])
        self.assertEqual(exit_code, 0)

    def test_enum_values(self):
        exit_code, output = self.run_all(testargs=["enumvalues"])
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()