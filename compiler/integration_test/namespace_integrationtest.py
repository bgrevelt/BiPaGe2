from integration_test.integrationtest import IntegrationTest
import unittest

class Namespace(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)

        self.write_bipage_file('''namespace Test.Integration.NSpace;
        Foo
        {
            field1: s32;  // Some info
            field2: f64;  // About 
            field3: u8;   // These fields
        }

        Bar
        {
            /*
            A
            multi
            line
            comment
            */
            Corey: int8;
            Max: float32;
            James : uint64;
            Billy : uint64;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "namespace_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int32_t>(-35643));
    p = serialize(p, 1.234);
    p = serialize(p, static_cast<std::uint8_t>(33));

    Test::Integration::NSpace::Foo_view parsed(buffer);

    check_equal(parsed.field1(), -35643);
    check_equal(parsed.field2(), 1.234);
    check_equal(parsed.field3(), 33);
    check_equal(parsed.size(), 13);
}

void test_bar_view()
{
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int8_t>(-25));
    p = serialize(p, 1.234f);
    p = serialize(p, static_cast<std::int64_t>(std::numeric_limits<int64_t>::max()));
    p = serialize(p, static_cast<std::int64_t>(std::numeric_limits<int64_t>::min()));

    Test::Integration::NSpace::Bar_view parsed(buffer);

    check_equal(parsed.Corey(), -25);
    check_equal(parsed.Max(), 1.234f);
    check_equal(parsed.James(), uint64_t(std::numeric_limits<int64_t>::max()));
    check_equal(parsed.Billy(), uint64_t(std::numeric_limits<int64_t>::min()));
    check_equal(parsed.size(), 21);
}

void test_foo_builder()
{
    int32_t field1 = 12345;
    double field2 = 123.456;
    uint8_t field3 = 255;
    Test::Integration::NSpace::Foo_builder builder(field1, field2, field3);

    std::vector<uint8_t> expected(13);
    auto p = expected.data();
    p = serialize(p, static_cast<std::int32_t>(12345));
    p = serialize(p, 123.456);
    serialize(p, static_cast<std::uint8_t>(255));

    auto result = builder.build();
    check_equal(result, expected);
}

void test_bar_builder()
{
    int8_t Corey = -128;
    float Max = 123.456;
    uint64_t James = std::numeric_limits<int64_t>::max();
    uint64_t Billy = std::numeric_limits<int64_t>::min();

    Test::Integration::NSpace::Bar_builder builder; // default ctor.
    // All values should be default initialized to zero.
    std::vector<uint8_t> expected(21, 0);
    check_equal(builder.build(), expected);

    builder.Corey(Corey);
    builder.Max(Max);
    builder.James(James);
    builder.Billy(Billy);

    auto p = expected.data();
    p = serialize(p, Corey);
    p = serialize(p, Max);
    p = serialize(p, James);
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