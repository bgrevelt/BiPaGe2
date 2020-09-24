import unittest
from subprocess import call
import os
import shutil

class Simple(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Simple, self).__init__(*args, **kwargs)
        self.python = "python3.8"
        self.bipage_path = "../bipage.py"
        self.test_name = "simple_integrationtest"

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
            field1: int32;
            field2: float64;
            field3 : uint8;
        }
        
        Bar
        {
            field1: int8;
            field2: float32;
            field3 : uint64;
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
        #include "../check.hpp"
        
        void test_foo_view()
        {
            std::uint8_t buffer[1024];
            auto p = buffer;
            p = serialize(p, static_cast<std::int32_t>(-35643));
            p = serialize(p, 1.234);
            p = serialize(p, static_cast<std::uint8_t>(33));

            const BiPaGe::Foo_view& parsed = BiPaGe::ParseFoo(buffer);

            check_equal(parsed.field1(), -35643);
            check_equal(parsed.field2(), 1.234);
            check_equal(parsed.field3(), 33);
        }
        
        void test_bar_view()
        {
            // TODO
        }
        
        void test_foo_builder()
        {
            // TODO
        }
        
        void test_bar_builder()
        {
            // TODO
        }


        int main(int argc, char* argv[])
        {
            test_foo_view();
        }''')


if __name__ == '__main__':
    unittest.main()