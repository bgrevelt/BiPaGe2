import unittest
from integration_test.integrationtest import IntegrationTest


class NonStandardSizeBigEndian(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        @bigendian;
        Foo
        {
            {
            field1: s12;  
            field2: u20;  
            }
            field3: f64;
            {
            field4_1: flag;
            field4_2: flag;
            field5: s4;
            field6: s18;  
            field7: u24;
            field8: s16;
            }
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "non_standard_size_big_endian_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    /*
    {
        field1: s12;  
        field2: u20;  
    }
    field3: f64;
    {
        field4_1: flag;
        field4_2: flag;
        field5: s4;
        field6: s18;  
        field7: u24;
        field8: s16;
    }
    
    Let's set some values
    field1: -150 --> 0xf6a
    field2: 1000000 --> 0xf4240
    field3: let's leave those zero for now
    field4_1: 1;
    field4_2: 0;
    field5: 0x8 --> -8
    field6: 0x217B8 -125000 // This one is especially confusing since an 18 bit field does not really exist. So conversion tools will tell us the most significant nibble is E, but in reality we only have two bits, so it's really 2  
    field7: 12500000 --> 0xBEBC20
    field8: 0
    
    That makes 3 encapsulating types
    - 32 bit field          0xf4240f6a
    - 64 bit float field    0x0000000000000000
    - 64 bit field          0x0000BEBC2085EE21
    
    Those encapsulating types get byte swapped because we use big endian
    - 32 bit field          0x6A0F24F4
    - 64 bit float field    0x0000000000000000
    - 64 bit field          0x23EE8520BCBE0000
    
    putting it al together:
    0x23EE8520BCBE000000000000000000006A0F24F4
    */
    
    
    std::vector<std::uint8_t> buffer { 0xF4, 0x24, 0x0F, 0x6A, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xBE, 0xBC, 0x20, 0x85, 0xEE, 0x21 };
    // We make an exception for the double and set that to something sensible    
    *reinterpret_cast<double*>(buffer.data() + 4) = naive_swap(-123.456);

    Foo_view parsed(buffer.data());

    check_equal(parsed.field1(), -150);
    check_equal(parsed.field2(), 1000000);
    check_equal(parsed.field3(), -123.456);
    check_equal(parsed.field4_1(), true);
    check_equal(parsed.field4_2(), false);
    check_equal(parsed.field5(), -8);
    check_equal(parsed.field6(), -125000);
    check_equal(parsed.field7(), 12500000);
    check_equal(parsed.field8(), 0);
    check_equal(parsed.size_in_bytes(), 20);
}

void test_foo_builder()
{
    
    std::int16_t field1 = -150;
    std::uint32_t field2 = 1000000;
    double field3 = -123.456;
    bool field4_1 = true;
    bool field4_2 = false;
    std::int8_t field5 = -8;
    std::int32_t field6 = -125000;
    std::uint32_t field7 = 12500000;
    std::int16_t field8 = 0;
    Foo_builder builder(field1, field2, field3, field4_1, field4_2, field5, field6, field7, field8);

    // See the view test for details on the expected data
    std::vector<std::uint8_t> expected { 0xF4, 0x24, 0x0F, 0x6A, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xBE, 0xBC, 0x20, 0x85, 0xEE, 0x21 };
    *reinterpret_cast<double*>(expected.data() + 4) = naive_swap(-123.456);
     
    auto result = builder.build();
    check_equal(result, expected);
}

void test_foo_builder2()
{
    
    std::int16_t field1 = -150;
    std::uint32_t field2 = 1000000;
    double field3 = -123.456;
    std::int8_t field5 = -8;
    std::int32_t field6 = -125000;
    std::uint32_t field7 = 12500000;
    std::int16_t field8 = 0;
    
    Foo_builder builder;
    builder.field1(field1);
    builder.field2(field2);
    builder.field3(field3);
    builder.field4_1(true);
    builder.field4_2(false);
    builder.field5(field5);
    builder.field6(field6);
    builder.field7(field7);
    builder.field8(field8);

    // See the view test for details on the expected data
    std::vector<std::uint8_t> expected { 0xF4, 0x24, 0x0F, 0x6A, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xBE, 0xBC, 0x20, 0x85, 0xEE, 0x21 };
    *reinterpret_cast<double*>(expected.data() + 4) = naive_swap(-123.456);
     
    auto result = builder.build();
    check_equal(result, expected);
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "fooview") == 0)
        test_foo_view();
    if(strcmp(argv[1], "foobuilder") == 0)
        test_foo_builder();
    if(strcmp(argv[1], "foobuilder2") == 0)
        test_foo_builder2();
}''')

    def test_view(self):
        exit_code, output = self.run_all(testargs=["fooview"])
        self.assertEqual(exit_code, 0)

    def test_builder(self):
        exit_code, output = self.run_all(testargs=["foobuilder"])
        self.assertEqual(exit_code, 0)

    def test_builder2(self):
        exit_code, output = self.run_all(testargs=["foobuilder2"])
        self.assertEqual(exit_code, 0)

if __name__ == '__main__':
    unittest.main()