import unittest
from subprocess import call
import os
import shutil


class Simple(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Simple, self).__init__(*args, **kwargs)
        self.python = "python3.8"
        self.bipage_path = "../bipage.py"
        self.test_name = "non_standard_size_misaligned_standard_type_integrationtest"

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
            {
                field1: u4;  
                field2: u16;  
                field3: u12;
            }
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
    const BiPaGe::Foo_view& parsed = BiPaGe::ParseFoo(buffer.data());
    
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
    
    BiPaGe::Foo_builder builder(field1, field2, field3);
    
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
    
    BiPaGe::Foo_builder builder;
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


if __name__ == '__main__':
    unittest.main()