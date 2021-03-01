import unittest
from integration_test.integrationtest import IntegrationTest

class ToString(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)

        self.write_bipage_file('''
        SomeEnum : u8
        {
            one = 1,
            two = 2,
            five = 5,
            nine = 9,
            twofiftyfive = 255
        }
        
        Foo
        {
            field: s32;  
            another_field_name_nice_and_long: f64;
            enum1: SomeEnum;
            enum2: SomeEnum;
            enum3: SomeEnum;
            enum4: SomeEnum;
            enum5: SomeEnum;
            {
                flag1: flag;
                flag2: flag;
                filler: u6;
            }
            collection: f32[6];
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "tostring_integrationtest_generated.h"
#include <iostream>
#include "../check.hpp"

void test_simple()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int32_t>(-35643));
    p = serialize(p, 1.234);
    p = serialize(p, SomeEnum::one);
    p = serialize(p, SomeEnum::two);
    p = serialize(p, SomeEnum::five);
    p = serialize(p, SomeEnum::nine);
    p = serialize(p, SomeEnum::twofiftyfive);
    p = serialize(p, static_cast<std::uint8_t>(0x02));
    p = serialize(p, 1.23f);
    p = serialize(p, 2.34f);
    p = serialize(p, 3.45f);
    p = serialize(p, 4.56f);
    p = serialize(p, 5.67f);
    p = serialize(p, 6.78f);

    Foo_view parsed(buffer);
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
        with open(f'temp_{self.test_name}/tostring_integrationtest_generated.h') as f:
            generated = f.read()
            self.assertFalse('std::string to_string() const' in generated)

    def test_simple(self):
        print(f'Starting {self.test_name}')

        exit_code, output = self.run_all(testargs=["simple"])
        self.check_output(output, '''
                field: -35643
                another_field_name_nice_and_long: 1.234
                enum1: SomeEnum::one (1)
                enum2: SomeEnum::two (2)
                enum3: SomeEnum::five (5)
                enum4: SomeEnum::nine (9)
                enum5: SomeEnum::twofiftyfive (255)
                flag1: cleared
                flag2: set
                filler: 0
                collection: [1.23, 2.34, 3.45, 4.56, 5.67, 6.78]''')

    def check_output(self, expected, output):
        # check two strings ignoring whitespace and casing
        output = ''.join(output.split()).lower()
        expected = ''.join(expected.split()).lower()
        self.assertEqual(output, expected)
