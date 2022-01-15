import unittest
from integration_test.integrationtest import IntegrationTest

class SimpleEnum(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        Enum1 : s32
        {
            Enum1_1 = -2147483648,
            Enum1_2 = -1718428315,
            Enum1_3 = -219666713,
            Enum1_4 = 428032383,
            Enum1_5 = 1054684538,
            Enum1_6 = 1268025781,
            Enum1_7 = 1378514902,
            Enum1_8 = 2082658223,
            Enum1_9 = 2147483647
        }
        Enum2 : u8
        {
            Enum2_1 = 0,
            Enum2_2 = 23,
            Enum2_3 = 58,
            Enum2_4 = 101,
            Enum2_5 = 123,
            Enum2_6 = 175,
            Enum2_7 = 180,
            Enum2_8 = 236,
            Enum2_9 = 255
        }
        Foo
        {
            field1: Enum1;
            field2: Enum1;
            field3: Enum1;
            field4: Enum1;
            field5: Enum1;
            field6: Enum1;
            field7: Enum1;
            field8: Enum1;
            field9: Enum1;
            field10: f64; 
            field11: Enum2;
            field12: Enum2;
            field13: Enum2;
            field14: Enum2;
            field15: Enum2;
            field16: Enum2;
            field17: Enum2;
            field18: Enum2;
            field19: Enum2;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "simple_enum_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_enum_values()
{
    check_equal(static_cast<int>(Enum1::Enum1_1), -2147483648);
    check_equal(static_cast<int>(Enum1::Enum1_2), -1718428315);
    check_equal(static_cast<int>(Enum1::Enum1_3), -219666713);
    check_equal(static_cast<int>(Enum1::Enum1_4), 428032383);
    check_equal(static_cast<int>(Enum1::Enum1_5), 1054684538);
    check_equal(static_cast<int>(Enum1::Enum1_6), 1268025781);
    check_equal(static_cast<int>(Enum1::Enum1_7), 1378514902);
    check_equal(static_cast<int>(Enum1::Enum1_8), 2082658223);
    check_equal(static_cast<int>(Enum1::Enum1_9), 2147483647);
    
    check_equal(static_cast<int>(Enum2::Enum2_1), 0);       
    check_equal(static_cast<int>(Enum2::Enum2_2), 23);      
    check_equal(static_cast<int>(Enum2::Enum2_3), 58);      
    check_equal(static_cast<int>(Enum2::Enum2_4), 101);     
    check_equal(static_cast<int>(Enum2::Enum2_5), 123);     
    check_equal(static_cast<int>(Enum2::Enum2_6), 175);     
    check_equal(static_cast<int>(Enum2::Enum2_7), 180);     
    check_equal(static_cast<int>(Enum2::Enum2_8), 236);     
    check_equal(static_cast<int>(Enum2::Enum2_9), 255);     
}

void test_foo_view()
{            
    
    std::uint8_t buffer[1024];
    auto p = buffer;
    
    p = serialize(p, Enum1::Enum1_1);
    p = serialize(p, Enum1::Enum1_2);
    p = serialize(p, Enum1::Enum1_3);
    p = serialize(p, Enum1::Enum1_4);
    p = serialize(p, Enum1::Enum1_5);
    p = serialize(p, Enum1::Enum1_6);
    p = serialize(p, Enum1::Enum1_7);
    p = serialize(p, Enum1::Enum1_8);
    p = serialize(p, Enum1::Enum1_9);
    p = serialize(p, 1.234);
    p = serialize(p, Enum2::Enum2_1);
    p = serialize(p, Enum2::Enum2_2);
    p = serialize(p, Enum2::Enum2_3);
    p = serialize(p, Enum2::Enum2_4);
    p = serialize(p, Enum2::Enum2_5);
    p = serialize(p, Enum2::Enum2_6);
    p = serialize(p, Enum2::Enum2_7);
    p = serialize(p, Enum2::Enum2_8);
    p = serialize(p, Enum2::Enum2_9);

    Foo_view parsed(buffer);

    check_equal(parsed.field1(), Enum1::Enum1_1);
    check_equal(parsed.field2(), Enum1::Enum1_2);
    check_equal(parsed.field3(), Enum1::Enum1_3);
    check_equal(parsed.field4(), Enum1::Enum1_4);
    check_equal(parsed.field5(), Enum1::Enum1_5);
    check_equal(parsed.field6(), Enum1::Enum1_6);
    check_equal(parsed.field7(), Enum1::Enum1_7);
    check_equal(parsed.field8(), Enum1::Enum1_8);
    check_equal(parsed.field9(), Enum1::Enum1_9);
    check_equal(parsed.field10(), 1.234);
    check_equal(parsed.field11(), Enum2::Enum2_1);
    check_equal(parsed.field12(), Enum2::Enum2_2);
    check_equal(parsed.field13(), Enum2::Enum2_3);
    check_equal(parsed.field14(), Enum2::Enum2_4);
    check_equal(parsed.field15(), Enum2::Enum2_5);
    check_equal(parsed.field16(), Enum2::Enum2_6);
    check_equal(parsed.field17(), Enum2::Enum2_7);
    check_equal(parsed.field18(), Enum2::Enum2_8);
    check_equal(parsed.field19(), Enum2::Enum2_9);
    check_equal(parsed.size(), 53);
}

void test_foo_builder()
{
    Foo_builder builder(
        Enum1::Enum1_1,
        Enum1::Enum1_2,
        Enum1::Enum1_3,
        Enum1::Enum1_4,
        Enum1::Enum1_5,
        Enum1::Enum1_6,
        Enum1::Enum1_7,
        Enum1::Enum1_8,
        Enum1::Enum1_9, 
        123.456, 
        Enum2::Enum2_1,
        Enum2::Enum2_2,
        Enum2::Enum2_3,
        Enum2::Enum2_4,
        Enum2::Enum2_5,
        Enum2::Enum2_6,
        Enum2::Enum2_7,
        Enum2::Enum2_8,
        Enum2::Enum2_9);
    
    std::vector<uint8_t> expected(53);
    auto p = expected.data();
    p = serialize(p, Enum1::Enum1_1);  
    p = serialize(p, Enum1::Enum1_2);  
    p = serialize(p, Enum1::Enum1_3);  
    p = serialize(p, Enum1::Enum1_4);  
    p = serialize(p, Enum1::Enum1_5);  
    p = serialize(p, Enum1::Enum1_6);  
    p = serialize(p, Enum1::Enum1_7);  
    p = serialize(p, Enum1::Enum1_8);  
    p = serialize(p, Enum1::Enum1_9);  
    p = serialize(p, 123.456);           
    p = serialize(p, Enum2::Enum2_1);  
    p = serialize(p, Enum2::Enum2_2);  
    p = serialize(p, Enum2::Enum2_3);  
    p = serialize(p, Enum2::Enum2_4);  
    p = serialize(p, Enum2::Enum2_5);  
    p = serialize(p, Enum2::Enum2_6);  
    p = serialize(p, Enum2::Enum2_7);  
    p = serialize(p, Enum2::Enum2_8);  
    p = serialize(p, Enum2::Enum2_9);  
    
    auto result = builder.build();
    check_equal(result, expected);
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "enumvalues") == 0)
        test_enum_values();
    if(strcmp(argv[1], "fooview") == 0)
        test_foo_view();
    if(strcmp(argv[1], "foobuild") == 0)
        test_foo_builder();
}''')

    def test_foo_view(self):
        exit_code, output = self.run_all(testargs=["fooview"])
        self.assertEqual(exit_code, 0)

    def test_foo_builder(self):
        exit_code, output = self.run_all(testargs=["foobuild"])
        self.assertEqual(exit_code, 0)

    def test_enum_values(self):
        exit_code, output = self.run_all(testargs=["enumvalues"])
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()