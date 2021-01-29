import unittest
from subprocess import call
import os
import shutil


class Simple(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Simple, self).__init__(*args, **kwargs)
        self.python = "python3.8"
        self.bipage_path = "../bipage.py"
        self.test_name = os.path.splitext(os.path.basename(__file__))[0]

        if os.path.exists('temp/'):
            shutil.rmtree('temp')
        os.mkdir('temp')

    def test_simple(self):
        self.write_bipage_file()
        self.write_cmake_file()
        self.write_test_cpp_file()

        self.run_test()

    def run_test(self):
        call([self.python, self.bipage_path, "-i", f"temp/{self.test_name}.bp", '-o', 'temp'])
        call(["cmake", "./"], cwd='temp/')
        call(["cmake", "--build", "."], cwd='temp/')
        rval = call(f"temp/{self.test_name}")
        self.assertEqual(rval, 0)

    def write_bipage_file(self):
        with open(f'temp/{self.test_name}.bp', 'w+') as f:
            f.write('''namespace Test.Integration.NSpace;
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

    def write_cmake_file(self):
        with open(f'temp/CMakeLists.txt', 'w+') as f:
            f.write(f'''
        cmake_minimum_required(VERSION 3.4)

        # set the project name
        project(integration_test)

        # add the executable
        add_executable({self.test_name} {self.test_name}.cpp)

        # specify the C++ standard
        set(CMAKE_CXX_STANDARD 11)
        set(CMAKE_CXX_STANDARD_REQUIRED True)
        set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} -std=c++11")''')

    def write_test_cpp_file(self):
        with open(f'temp/{self.test_name}.cpp', 'w+') as f:
            f.write('''
#include "Foo_generated.h"
#include "Bar_generated.h"
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

    const Test::Integration::NSpace::Foo_view& parsed = Test::Integration::NSpace::ParseFoo(buffer);

    check_equal(parsed.field1(), -35643);
    check_equal(parsed.field2(), 1.234);
    check_equal(parsed.field3(), 33);
}

void test_bar_view()
{
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int8_t>(-25));
    p = serialize(p, 1.234f);
    p = serialize(p, static_cast<std::int64_t>(std::numeric_limits<int64_t>::max()));
    p = serialize(p, static_cast<std::int64_t>(std::numeric_limits<int64_t>::min()));

    const Test::Integration::NSpace::Bar_view& parsed = Test::Integration::NSpace::ParseBar(buffer);

    check_equal(parsed.Corey(), -25);
    check_equal(parsed.Max(), 1.234f);
    check_equal(parsed.James(), uint64_t(std::numeric_limits<int64_t>::max()));
    check_equal(parsed.Billy(), uint64_t(std::numeric_limits<int64_t>::min()));
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
    test_foo_view();
    test_bar_view();
    test_foo_builder();
    test_bar_builder();
}''')


if __name__ == '__main__':
    unittest.main()