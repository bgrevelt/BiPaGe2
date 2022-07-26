import unittest
from compiler.integration_test.integrationtest import IntegrationTest

class CollectionEnum(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)
        self.write_bipage_file('''
        MyEnum : u16
        {
            red = 0,
            green = 1,
            blue = 2
        }
        
        Foo
        {
            field1: s32;
            field2: MyEnum[3];
            field3: f64;
            field4: u8;
        }
        ''')
        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "collection_enum_integrationtest_generated.h"
#include <iostream>
#include <vector>
#include <limits>
#include "../check.hpp"

void test_foo_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int32_t>(-35643));
    
    std::vector<MyEnum> field2_values {MyEnum::red,MyEnum::green,MyEnum::blue};
        
    for(size_t i=0 ; i<field2_values.size() ; ++i)
        p = serialize(p, static_cast<std::uint16_t>(field2_values[i]));
    
    p = serialize(p, 1.234);
    p = serialize(p, static_cast<std::uint8_t>(33));

    Foo_view parsed(buffer);

    check_equal(parsed.field1(), -35643);
    auto collection = parsed.field2();
    check_equal(collection.size(), field2_values.size());
    for(size_t i = 0 ; i < collection.size() ; ++i)
    {
        check_equal(collection[i], field2_values[i]);
    }
    check_equal(parsed.field3(), 1.234);
    check_equal(parsed.field4(), 33);
    check_equal(parsed.size_in_bytes(), 19);
}

void test_foo_builder()
{
    int32_t field1 = 12345;
    std::vector<MyEnum> field2 {MyEnum::red,MyEnum::green,MyEnum::blue};
    double field3 = 123.456;
    uint8_t field4 = 255;
    Foo_builder builder(field1, field2, field3, field4);
    
    std::vector<uint8_t> expected(19);
    auto p = expected.data();
    p = serialize(p, static_cast<std::int32_t>(12345));
     for(size_t i=0 ; i<field2.size() ; ++i)
        p = serialize(p, static_cast<std::uint16_t>(field2[i]));
    p = serialize(p, 123.456);
    serialize(p, static_cast<std::uint8_t>(255));
    
    auto result = builder.build();
    check_equal(result, expected);
}

void test_foo_string()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int32_t>(-35643));
    
    std::vector<MyEnum> field2_values {MyEnum::red,MyEnum::green,MyEnum::blue};
        
    for(size_t i=0 ; i<field2_values.size() ; ++i)
        p = serialize(p, static_cast<std::uint16_t>(field2_values[i]));
    
    p = serialize(p, 1.234);
    p = serialize(p, static_cast<std::uint8_t>(33));

    Foo_view parsed(buffer);

    std::cout << parsed.to_string() << std::endl;
}



int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "view") == 0)
        test_foo_view();
    if(strcmp(argv[1], "build") == 0)
        test_foo_builder();
    if(strcmp(argv[1], "tostring") == 0)
        test_foo_string();
}''')

    def test_foo_view(self):
        exit_code, output = self.run_all(testargs=["view"])
        self.assertEqual(exit_code, 0)

    def test_foo_builder(self):
        exit_code, output = self.run_all(testargs=["build"])
        self.assertEqual(exit_code, 0)

    def test_foo_to_string(self):
        exit_code, output = self.run_all(testargs=["tostring"])
        self.check_output(output, '''
                        field1: -35643
                        field2: [myenum::red(0), myenum::green(1), myenum::blue(2)]
                        field3: 1.234
                        field4: 33''')


if __name__ == '__main__':
    unittest.main()