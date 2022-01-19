import unittest
from integration_test.integrationtest import IntegrationTest

class NestedDataTypeCollection(unittest.TestCase, IntegrationTest):

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
            f2: Foo[f1];
            f3: f64;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "nested_data_type_collection_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

std::uint8_t* AddFoo(std::uint8_t* p, std::int32_t field1, std::uint16_t field3, const std::vector<std::uint8_t>& field4, double field5)
{
    p = serialize(p, field1);
    p += sizeof(float);
    p = serialize(p, field3);
    p = serialize(p, field4);
    p = serialize(p, field5);
    return p;
}

void test_bar_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    
    auto foo_field4_values1 = std::vector<std::uint8_t> {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30};
    auto foo_field4_values2 = std::vector<std::uint8_t> {50, 100, 150, 200, 250};
    auto foo_field4_values3 = std::vector<std::uint8_t> {0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233};
    
    p = serialize(p, static_cast<std::int32_t>(3));
    p = AddFoo(p, -20, 30, foo_field4_values1, 1.234);
    p = AddFoo(p, 287, 5, foo_field4_values2, 4.321);
    p = AddFoo(p, 763, 14, foo_field4_values3, 18.1920);
    p = serialize(p, 2.345);
    
    Bar_view parsed(buffer);
    
    check_equal(parsed.f1(), 3);
    
    check_equal(parsed.f2()[0].field1(), -20);
    check_equal(parsed.f2()[0].field3(), 30);
    check_equal(parsed.f2()[0].field4(), foo_field4_values1);
    check_equal(parsed.f2()[0].field5(), 1.234);
    
    check_equal(parsed.f2()[1].field1(), 287);
    check_equal(parsed.f2()[1].field3(), 5);
    check_equal(parsed.f2()[1].field4(), foo_field4_values2);
    check_equal(parsed.f2()[1].field5(), 4.321);
    
    check_equal(parsed.f2()[2].field1(), 763);
    check_equal(parsed.f2()[2].field3(), 14);
    check_equal(parsed.f2()[2].field4(), foo_field4_values3);
    check_equal(parsed.f2()[2].field5(), 18.1920);
    
    check_equal(parsed.f3(), 2.345);
    check_equal(parsed.size_in_bytes(), 115);
}

void test_bar_builder()
{
    std::int32_t Foo1_field1 = -20;
    std::uint16_t Foo1_field3 = 30;
    std::vector<std::uint8_t> Foo1_field4 {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30};
    double Foo1_field5 = 1.234;
    
    std::int32_t Foo2_field1 = 287;
    std::uint16_t Foo2_field3 = 5;
    std::vector<std::uint8_t> Foo2_field4 {50, 100, 150, 200, 250};
    double Foo2_field5 = 4.321;
    
    std::int32_t Foo3_field1 = 763;
    std::uint16_t Foo3_field3 = 14;
    std::vector<std::uint8_t> Foo3_field4 {0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233};
    double Foo3_field5 = 18.1920;
    
    std::int32_t Bar_field1 = 3;
    std::vector<Foo_builder> Bar_field2 {
        Foo_builder(Foo1_field1, Foo1_field3, Foo1_field4, Foo1_field5),
        Foo_builder(Foo2_field1, Foo2_field3, Foo2_field4, Foo2_field5),
        Foo_builder(Foo3_field1, Foo3_field3, Foo3_field4, Foo3_field5)
    };
    double Bar_field3 = 2.345;
    
    Bar_builder builder(Bar_field1, Bar_field2, Bar_field3);
    
    std::vector<uint8_t> expected(115);
    auto p = expected.data();
    p = serialize(p, Bar_field1);
    
    p = AddFoo(p, Foo1_field1, Foo1_field3, Foo1_field4, Foo1_field5);
    p = AddFoo(p, Foo2_field1, Foo2_field3, Foo2_field4, Foo2_field5);
    p = AddFoo(p, Foo3_field1, Foo3_field3, Foo3_field4, Foo3_field5);
    
    p = serialize(p, Bar_field3);
    
    auto result = builder.build();
    check_equal(result, expected);
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "view") == 0)
        test_bar_view();
    if(strcmp(argv[1], "build") == 0)
        test_bar_builder();
}''')

    def test_foo_view(self):
        exit_code, output = self.run_all(bipageargs=['--cpp-17'], testargs=["view"])
        self.assertEqual(exit_code, 0)

    def test_foo_builder(self):
        exit_code, output = self.run_all(bipageargs=['--cpp-17'], testargs=["build"])
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()