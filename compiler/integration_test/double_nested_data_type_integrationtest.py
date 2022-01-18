import unittest
from integration_test.integrationtest import IntegrationTest

class DoubleNestedDataType(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        Foo
        {
            field1: s32;
            f32;
            field3: u16;
            field4: u8[field3];
            field5: f64;
        }
        Bar
        {
            f1: s32;
            f2: Foo;
            f3: f64;
        }
        FooBar
        {
            {
                f1: flag;
                f2: u7;
            }
            f3: Bar;
            f4: f64;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "double_nested_data_type_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foobar_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    
    auto foo_field4_values = std::vector<std::uint8_t> {
    1,2,3,4,5,6,7,8,9,10,
    11,12,13,14,15,16,17,18,19,20,
    21,22,23,24,25,26,27,28,29,30
    };
    
    p = serialize(p, static_cast<std::uint8_t>(0xfe));       // FooBar::f1&f2
    p = serialize(p, static_cast<std::int32_t>(8));         // Bar::f1
    p = serialize(p, static_cast<std::int32_t>(-20));       // Foo::field1
    p += sizeof(float);                                     // Foo::padding
    p = serialize(p, static_cast<std::uint16_t>(30));       // Foo::field3
    p = serialize(p, foo_field4_values);                    // Foo::field4
    p = serialize(p, 1.234);                                // Foo::field5
    p = serialize(p, 2.345);                                // Bar::f3
    p = serialize(p, 3.456);                                // FooBar::f4
    
    FooBar_view parsed(buffer);
    
    check_equal(parsed.f1(), false);
    check_equal(parsed.f2(), 127);
    check_equal(parsed.f3().f1(), 8);
    check_equal(parsed.f3().f2().field1(), -20);
    check_equal(parsed.f3().f2().field3(), 30);
    check_equal(parsed.f3().f2().field4(), foo_field4_values);
    check_equal(parsed.f3().f2().field5(), 1.234);
    check_equal(parsed.f3().f3(), 2.345);
    check_equal(parsed.f4(), 3.456);
    
    check_equal(parsed.size_in_bytes(), 69);
}

void test_foobar_builder()
{
    std::int32_t Foo_field1 = 1234567;
    std::uint16_t Foo_field3 = 65534;
    std::vector<std::uint8_t> Foo_field4 {
    1,2,3,4,5,6,7,8,9,10,
    11,12,13,14,15,16,17,18,19,20,
    21,22,23,24,25,26,27,28,29,30
    };
    double Foo_field5 = 1.234;
    
    
    std::int32_t Bar_field1 = -12345;
    Foo_builder Bar_field2(Foo_field1, Foo_field3, Foo_field4, Foo_field5);
    double Bar_field3 = 2.345;
    
    bool foo_bar_f1 = false;
    std::uint8_t foo_bar_f2 = 127;
    Bar_builder foo_bar_f3(Bar_field1, Bar_field2, Bar_field3);
    double foo_bar_f4 = 3.456;
    
    FooBar_builder builder(foo_bar_f1, foo_bar_f2, foo_bar_f3, foo_bar_f4);
    
    std::vector<uint8_t> expected(69);
    auto p = expected.data();
    p = serialize(p, static_cast<std::uint8_t>(foo_bar_f2<<1));
    p = serialize(p, Bar_field1);
    p = serialize(p, Foo_field1);
    p += sizeof(float);
    p = serialize(p, Foo_field3);
    p = serialize(p, Foo_field4);
    p = serialize(p, Foo_field5);
    p = serialize(p, Bar_field3);
    p = serialize(p, foo_bar_f4);
    
    auto result = builder.build();
    check_equal(result, expected);
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "view") == 0)
        test_foobar_view();
    if(strcmp(argv[1], "build") == 0)
        test_foobar_builder();
}''')

    def test_foo_view(self):
        exit_code, output = self.run_all(bipageargs=['--cpp-17'], testargs=["view"])
        self.assertEqual(exit_code, 0)

    def test_foo_builder(self):
        exit_code, output = self.run_all(bipageargs=['--cpp-17'], testargs=["build"])
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()