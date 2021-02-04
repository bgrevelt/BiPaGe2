import unittest
from integrationtest import IntegrationTest
import subprocess

class ToString(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)

        self.write_bipage_file('''
        Foo
        {
            field: s32;  
            another_field_name_nice_and_long: f64;
            a_byte: u8;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
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



    def test_no_to_string(self):
        # Validate method is not generated if disabled in bigpage arguments
        self.run_bipage(['--cpp-no-to-string'])
        generated = open(f'temp_{self.test_name}/Foo_generated.h').read()
        self.assertFalse('to_string' in generated)

    def test_simple(self):
        print(f'Starting {self.test_name}')

        exit_code, output = self.run_all(testargs=["simple"])
        self.check_output(output, '''
                field: -35643
                another_field_name_nice_and_long: 1.234
                a_byte: 33''')

    def check_output(self, expected, output):
        # check two strings ignoring whitespace and casing
        output = ''.join(output.split()).lower()
        expected = ''.join(expected.split()).lower()
        self.assertEqual(output, expected)
