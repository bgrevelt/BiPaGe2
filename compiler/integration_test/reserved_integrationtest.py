import unittest
from integrationtest import IntegrationTest


class Reserved(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        Foo
        {
            field1: s32;  // Same as simple
            f64;          // But with a reserved field
            field3: u8;   
        }

        Bar
        {
            Corey: int8;
            float32;
            uint64;
            Billy : uint64;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "reserved_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int32_t>(-35643));
    p = serialize(p, 0.0);
    p = serialize(p, static_cast<std::uint8_t>(33));

    Foo_view parsed(buffer);

    check_equal(parsed.field1(), -35643);
    check_equal(parsed.field3(), 33);
}

void test_bar_view()
{
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int8_t>(-25));
    p = serialize(p, 0.0f);
    p = serialize(p, static_cast<std::int64_t>(0));
    p = serialize(p, static_cast<std::int64_t>(std::numeric_limits<int64_t>::min()));

    Bar_view parsed(buffer);

    check_equal(parsed.Corey(), -25);
    check_equal(parsed.Billy(), uint64_t(std::numeric_limits<int64_t>::min()));
}

void test_foo_builder()
{
    int32_t field1 = 12345;
    uint8_t field3 = 255;
    Foo_builder builder(field1, field3);

    std::vector<uint8_t> expected(13);
    auto p = expected.data();
    p = serialize(p, static_cast<std::int32_t>(12345));
    p += sizeof(double);
    serialize(p, static_cast<std::uint8_t>(255));

    auto result = builder.build();
    check_equal(result, expected);
}

void test_bar_builder()
{
    int8_t Corey = -128;
    uint64_t Billy = std::numeric_limits<int64_t>::min();

    Bar_builder builder; // default ctor.
    // All values should be default initialized to zero.
    std::vector<uint8_t> expected(21, 0);
    check_equal(builder.build(), expected);

    builder.Corey(Corey);
    builder.Billy(Billy);

    auto p = expected.data();
    p = serialize(p, Corey);
    p += sizeof(float);
    p += sizeof(uint64_t);
    serialize(p, Billy);

    check_equal(builder.build(), expected);
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "fooview") == 0)
        test_foo_view();
    if(strcmp(argv[1], "barview") == 0)
        test_bar_view();
    if(strcmp(argv[1], "foobuild") == 0)
        test_foo_builder();
    if(strcmp(argv[1], "barbuild") == 0)
        test_bar_builder();
}''')

    def test_foo_view(self):
        exit_code, output = self.run_all(testargs=["fooview"])
        self.assertEqual(exit_code, 0)

    def test_bar_view(self):
        exit_code, output = self.run_all(testargs=["barview"])
        self.assertEqual(exit_code, 0)

    def test_foo_builder(self):
        exit_code, output = self.run_all(testargs=["foobuild"])
        self.assertEqual(exit_code, 0)

    def test_bar_builder(self):
        exit_code, output = self.run_all(testargs=["barbuild"])
        self.assertEqual(exit_code, 0)

if __name__ == '__main__':
    unittest.main()