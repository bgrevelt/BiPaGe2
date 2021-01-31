import unittest
import subprocess
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

        self.write_bipage_file()
        self.write_cmake_file()
        self.write_test_cpp_file()

    def test_no_to_string(self):
        # Validate method is not generated if disabled in bigpage arguments
        self.run_bipage(['--cpp-no-to-string'])
        self.run_no_to_string()

    def test_simple(self):
        self.build_all()
        self.run_simple()

    def check_output(self, expected, output):
        # check two strings ignoring whitespace and casing
        output = ''.join(output.split()).lower()
        expected = ''.join(expected.split()).lower()
        self.assertEqual(output, expected)

    def run_bipage(self, args = None):
        to_execute = [self.python, self.bipage_path, "-i", f"temp/{self.test_name}.bp", '-o', 'temp']
        if args:
            to_execute.extend(args)
        subprocess.call(to_execute)

    def build_all(self, bipage_args = None):
        self.run_bipage(bipage_args)
        subprocess.call(["cmake", "./"], cwd='temp/')
        subprocess.call(["cmake", "--build", "."], cwd='temp/')

    def run_simple(self):
        result = subprocess.run([f"temp/{self.test_name}", 'simple'], stdout=subprocess.PIPE)
        self.check_output(result.stdout.decode('utf-8'), '''
        field: -35643
        another_field_name_nice_and_long: 1.234
        a_byte: 33''')

    def run_no_to_string(self):
        with open('temp/Foo_generated.h') as f:
            text = f.read()
            self.assertFalse('to_string' in text)

    def write_bipage_file(self):
        with open(f'temp/{self.test_name}.bp', 'w+') as f:
            f.write('''
        Foo
        {
            field: s32;  
            another_field_name_nice_and_long: f64;
            a_byte: u8;
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
#include "../check.hpp"

void test_simple()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int32_t>(-35643));
    p = serialize(p, 1.234);
    p = serialize(p, static_cast<std::uint8_t>(33));

    const Foo_view& parsed = ParseFoo(buffer);
    std::cout << parsed.to_string() << std::endl;
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "simple") == 0)
        test_simple();
}''')


if __name__ == '__main__':
    unittest.main()