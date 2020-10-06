import unittest
from subprocess import call
import os
import shutil


class Simple(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Simple, self).__init__(*args, **kwargs)
        self.python = "python3.8"
        self.bipage_path = "../bipage.py"
        self.test_name = "non-standard_size_integrationtest"

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
            field1: s12;  
            field2: u20;  
            field3: f64;
            field4: u2;
            field5: s4;
            field6: s18;  
            field7: u24;
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
    field1: s12;  
    field2: u20;  
    field3: f64;
    field4: u2;
    field5: s4;
    field6: s18; 
    field7: u24; 
    
    Let's set some values
    field1: -150 --> 0xf6a
    field2: 1000000 --> 0xf4240
    field3: let's leave those zero for now
    field4: 3 --> 0x3
    field5: 0x8 --> -8
    field6: 0x217B8 -125000 // This one is especially confusing since an 18 bit field does not really exist. So conversion tools will tell us the most significant nibble is E, but in reality we only have two bits, so it's really 2  
    field7: 12500000 --> 0xBEBC20
    
    if we look at all the bits together (top field right) we get this
    10111110 10111100 00100000 10000101 11101110 00100011 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 11110100 00100100 00001111 01101010
    +--------------------------+------------------++--+++ +---------------------------------------------------------------------------------------------------------------------------+ +--------------------++-----------+
             Field7                 Field6          F5 F4                                                   Field3                                                                             Field2            Field1
         
    which translated into hex becomes 0xbebc2085b7230000000000000000f4240f6a
    */
    
    std::vector<std::uint8_t> buffer { 0x6a, 0x0f, 0x24, 0xf4, 0, 0, 0, 0, 0, 0, 0, 0, 0x23, 0xee, 0x85, 0x20, 0xbc, 0xbe };
    // We make an exception for the double and set that to something sensible    
    *reinterpret_cast<double*>(buffer.data() + 4) = -123.456;

    const BiPaGe::Foo_view& parsed = BiPaGe::ParseFoo(buffer.data());

    check_equal(parsed.field1(), -150);
    check_equal(parsed.field2(), 1000000);
    check_equal(parsed.field3(), -123.456);
    check_equal(parsed.field4(), 3);
    check_equal(parsed.field5(), -8);
    check_equal(parsed.field6(), -125000);
    check_equal(parsed.field7(), 12500000);
}

void test_foo_builder()
{
    
    std::int16_t field1 = -150;
    std::uint32_t field2 = 1000000;
    double field3 = -123.456;
    std::uint8_t field4 = 3;
    std::int8_t field5 = -8;
    std::int32_t field6 = -125000;
    std::uint32_t field7 = 12500000;
    BiPaGe::Foo_builder builder(field1, field2, field3, field4, field5, field6, field7);

    // See the view test for details on the expected data
    std::vector<std::uint8_t> expected { 0x6a, 0x0f, 0x24, 0xf4, 0, 0, 0, 0, 0, 0, 0, 0, 0x23, 0xee, 0x85, 0x20, 0xbc, 0xbe };
    *reinterpret_cast<double*>(expected.data() + 4) = -123.456;
     
    auto result = builder.build();
    check_equal(result, expected);
}

void test_foo_builder2()
{
    
    std::int16_t field1 = -150;
    std::uint32_t field2 = 1000000;
    double field3 = -123.456;
    std::uint8_t field4 = 3;
    std::int8_t field5 = -8;
    std::int32_t field6 = -125000;
    std::uint32_t field7 = 12500000;
    
    BiPaGe::Foo_builder builder;
    builder.field1(field1);
    builder.field2(field2);
    builder.field3(field3);
    builder.field4(field4);
    builder.field5(field5);
    builder.field6(field6);
    builder.field7(field7);

    // See the view test for details on the expected data
    std::vector<std::uint8_t> expected { 0x6a, 0x0f, 0x24, 0xf4, 0, 0, 0, 0, 0, 0, 0, 0, 0x23, 0xee, 0x85, 0x20, 0xbc, 0xbe };
    *reinterpret_cast<double*>(expected.data() + 4) = -123.456;
     
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