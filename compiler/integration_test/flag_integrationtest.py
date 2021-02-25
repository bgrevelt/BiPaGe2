import unittest
from integration_test.integrationtest import IntegrationTest

class Simple(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        Foo
        {
            {
                field1 : s3;
                field2 : flag;
                field3 : u3;
                field4 : flag;
            }
            field5: s32;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "flag_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    
    /*
    field1 -3 --> b'101'
    field2 set --> b'1'
    field3 7 -> b'111
    field4 clear --> b'0'
    putting it together (most significant to least significant bit)
    01111101 -> 0x7D
    */
    
    p = serialize(p, static_cast<std::uint8_t>(0x7d));
    p = serialize(p, static_cast<std::int32_t>(-533));

    Foo_view parsed(buffer);

    check_equal(parsed.field1(), -3);
    check_equal(parsed.field2(), true);
    check_equal(parsed.field3(), 7);
    check_equal(parsed.field4(), false);
    check_equal(parsed.field5(), -533);
}


void test_foo_builder()
{
    Foo_builder builder(-3, true, 7, false, -533);
    
    std::vector<uint8_t> expected(5);
    
    auto p = expected.data();
    p = serialize(p, static_cast<std::uint8_t>(0x7d));
    p = serialize(p, static_cast<std::int32_t>(-533));
    
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

    def test_view(self):
        exit_code, output = self.run_all(testargs=["view"])
        self.assertEqual(exit_code, 0)

    def test_builder(self):
        exit_code, output = self.run_all(testargs=["build"])
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()