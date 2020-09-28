import unittest
from subprocess import call
import os
import shutil


class Simple(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Simple, self).__init__(*args, **kwargs)
        self.python = "python3.8"
        self.bipage_path = "../bipage.py"
        self.test_name = "reserved_integrationtest"

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
            f.write('''
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
    p = serialize(p, 0.0);
    p = serialize(p, static_cast<std::uint8_t>(33));

    const BiPaGe::Foo_view& parsed = BiPaGe::ParseFoo(buffer);

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

    const BiPaGe::Bar_view& parsed = BiPaGe::ParseBar(buffer);

    check_equal(parsed.Corey(), -25);
    check_equal(parsed.Billy(), uint64_t(std::numeric_limits<int64_t>::min()));
}

void test_foo_builder()
{
    int32_t field1 = 12345;
    uint8_t field3 = 255;
    BiPaGe::Foo_builder builder(field1, field3);

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

    BiPaGe::Bar_builder builder; // default ctor.
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
    test_foo_view();
    test_bar_view();
    test_foo_builder();
    test_bar_builder();
}''')


if __name__ == '__main__':
    unittest.main()