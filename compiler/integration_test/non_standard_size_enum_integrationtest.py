import unittest
from integration_test.integrationtest import IntegrationTest

class NonStandardSizeEnum(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        MyEnum1 : u2
        {
           Aap = 0,
           Noot = 1,
           Mies = 2,
           Vis = 3
        }
        
        MyEnum2 : s4
        {
           Lorem = -8,
           ipsum = -7,
           dolor = -6,
           sit = -5,
           amet = -4,
           consectetur = -3,
           adipiscing = -2,
           elit = -1,
           sed = 0,
           doo = 1, // Extra o to prevent using a keyword
           eiusmod = 2,
           tempor = 3,
           incididunt = 4,
           ut = 5,
           labore = 6,
           et = 7
        }
        
        Foo
        {
            {
            field1: s12;  
            field2: u20;  
            }
            field3: f64;
            {
            field4: MyEnum1;
            field5: MyEnum2;
            field6: s18;  
            field7: u24;
            field8: s16;
            }
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "non_standard_size_enum_integrationtest_generated.h"
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
    field8: s16;
    
    Let's set some values
    field1: -150 --> 0xf6a
    field2: 1000000 --> 0xf4240
    field3: let's leave those zero for now
    field4: 'Vis' (3) --> 0x3
    field5: 'Lorem' (-8) --> 0x8
    field6: 0x217B8 -125000 // This one is especially confusing since an 18 bit field does not really exist. So conversion tools will tell us the most significant nibble is E, but in reality we only have two bits, so it's really 2  
    field7: 12500000 --> 0xBEBC20
    field8: 0
    
    if we look at all the bits together (top field right) we get this
    00000000 00000000 10111110 10111100 00100000 10000101 11101110 00100011 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 11110100 00100100 00001111 01101010
    +-----------------+--------------------------+------------------++--+++ +---------------------------------------------------------------------------------------------------------------------------+ +--------------------++-----------+
           Field 8             Field7                 Field6          F5 F4                                                   Field3                                                                             Field2            Field1
         
    which translated into hex becomes 0xbebc2085b7230000000000000000f4240f6a
    */
    
    std::vector<std::uint8_t> buffer { 0x6a, 0x0f, 0x24, 0xf4, 0, 0, 0, 0, 0, 0, 0, 0, 0x23, 0xee, 0x85, 0x20, 0xbc, 0xbe, 0, 0 };
    // We make an exception for the double and set that to something sensible    
    *reinterpret_cast<double*>(buffer.data() + 4) = -123.456;

    Foo_view parsed(buffer.data());

    check_equal(parsed.field1(), -150);
    check_equal(parsed.field2(), 1000000);
    check_equal(parsed.field3(), -123.456);
    check_equal(parsed.field4(), MyEnum1::Vis);
    check_equal(parsed.field5(), MyEnum2::Lorem);
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
    MyEnum1 field4 = MyEnum1::Vis;
    MyEnum2 field5 = MyEnum2::Lorem;
    std::int32_t field6 = -125000;
    std::uint32_t field7 = 12500000;
    std::int16_t field8 = 0;
    Foo_builder builder(field1, field2, field3, field4, field5, field6, field7, field8);

    // See the view test for details on the expected data
    std::vector<std::uint8_t> expected { 0x6a, 0x0f, 0x24, 0xf4, 0, 0, 0, 0, 0, 0, 0, 0, 0x23, 0xee, 0x85, 0x20, 0xbc, 0xbe, 0, 0 };
    *reinterpret_cast<double*>(expected.data() + 4) = -123.456;
     
    auto result = builder.build();
    check_equal(result, expected);
}

void test_foo_builder2()
{
    
    std::int16_t field1 = -150;
    std::uint32_t field2 = 1000000;
    double field3 = -123.456;
    MyEnum1 field4 = MyEnum1::Vis;
    MyEnum2 field5 = MyEnum2::Lorem;
    std::int32_t field6 = -125000;
    std::uint32_t field7 = 12500000;
    std::int16_t field8 = 0;
    
    Foo_builder builder;
    builder.field1(field1);
    builder.field2(field2);
    builder.field3(field3);
    builder.field4(field4);
    builder.field5(field5);
    builder.field6(field6);
    builder.field7(field7);
    builder.field8(field8);

    // See the view test for details on the expected data
    std::vector<std::uint8_t> expected { 0x6a, 0x0f, 0x24, 0xf4, 0, 0, 0, 0, 0, 0, 0, 0, 0x23, 0xee, 0x85, 0x20, 0xbc, 0xbe, 0, 0 };
    *reinterpret_cast<double*>(expected.data() + 4) = -123.456;
     
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

    def test_foo_view(self):
        exit_code, output = self.run_all(
            testargs=["fooview"])
        self.assertEqual(exit_code, 0)

    def test_foo_builder(self):
        exit_code, output = self.run_all(
            testargs=["foobuilder"])
        self.assertEqual(exit_code, 0)

    def test_foo_builder2(self):
        exit_code, output = self.run_all(
            testargs=["foobuilder2"])
        self.assertEqual(exit_code, 0)

if __name__ == '__main__':
    unittest.main()