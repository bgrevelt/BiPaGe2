import unittest
from subprocess import call
import os
import shutil


class Simple(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Simple, self).__init__(*args, **kwargs)
        self.python = "python3.8"
        self.bipage_path = "../bipage.py"
        self.test_name = "non_standard_size_input_validation_integrationtest"

        self.clear_temp_dir()


    def clear_temp_dir(self):
        if os.path.exists('temp/'):
            shutil.rmtree('temp')
        os.mkdir('temp')

    def test_simple(self):
        # Normal bigage settings and writing invalid values: expect an exception
        self.write_bipage_file()
        self.write_cmake_file()
        self.write_test_cpp_file()
        self.run_test()

        # Compiler setting to not generate validation code and writing invalid values: don't expect an exception
        self.clear_temp_dir()
        self.write_bipage_file()
        self.write_cmake_file()
        self.write_test_cpp_file2()
        self.run_test(['--cpp-no-validate-builder-input'])

    def run_test(self, arguments = []):
        call([self.python, self.bipage_path, "-i", f"temp/{self.test_name}.bp", '-o', 'temp'] + arguments)
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
            field1: s12;  
            field2: u20;
            }  
            field3: f64;
            {
            field4: u2;
            field5: s4;
            field6: s18;  
            field7: u24;
            field8: s16;
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
#include "../check.hpp"
#include "Foo_generated.h"

void test_foo_builder()
{
    Foo_builder builder(0, 0, 0.0, 4, 0, 0, 0, 0); // 4 doesn't fit into u2
}

void test_foo_builder2()
{
    Foo_builder builder;
    builder.field1(-2049); // Doesn't fit into int12
}


int main(int argc, char* argv[])
{
    check_exception(std::runtime_error, []() { test_foo_builder(); });
    check_exception(std::runtime_error, []() { test_foo_builder2(); });
}''')

    def write_test_cpp_file2(self):
        with open(f'temp/{self.test_name}.cpp', 'w+') as f:
            f.write('''
    #include "../check.hpp"
    #include "Foo_generated.h"

    void test_foo_builder()
    {
        Foo_builder builder(0, 0, 0.0, 4, 0, 0, 0, 0); // 4 doesn't fit into u2
    }

    void test_foo_builder2()
    {
        Foo_builder builder;
        builder.field1(-2049); // Doesn't fit into int12
    }


    int main(int argc, char* argv[])
    {
        test_foo_builder();
        test_foo_builder2();
    }''')


if __name__ == '__main__':
    unittest.main()