import unittest
from compiler.integration_test.integrationtest import IntegrationTest


class ImportEnumNamepace(unittest.TestCase, IntegrationTest):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        IntegrationTest.__init__(self)

        self.write_bipage_file('''
        namespace name.space.one;
        SomeEnum : u8
        {
            one = 1,
            two = 2,
            five = 5,
            nine = 9,
            twofiftyfive = 255
        }
        ''', 'MyEnums.bp')

        self.write_bipage_file('''
        import "MyEnums.bp";
        namespace name.space.two;
        
        SomeEnum : u8
        {
            lorem = 0,
            ipsum = 1
        }
        
        Foo
        {
            field1 : s16;
            field2 : name.space.one.SomeEnum;
            field3 : SomeEnum;
            field4 : f64;
        }
        ''')


        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "enum_import_namespace_integrationtest_generated.h"
#include <iostream>
#include "../check.hpp"

void test_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int16_t>(-635));
    p = serialize(p, static_cast<std::uint8_t>(5));
    p = serialize(p, static_cast<std::uint8_t>(0));
    p = serialize(p, -123.456);

    name::space::two::Foo_view parsed(buffer);

    check_equal(parsed.field1(), -635);
    check_equal(parsed.field2(), name::space::one::SomeEnum::five);
    check_equal(parsed.field3(), name::space::two::SomeEnum::lorem);
    check_equal(parsed.field4(), -123.456);
    check_equal(parsed.size_in_bytes(), 12);
}

void test_builder()
{
    int16_t field1 = 12345;
    name::space::one::SomeEnum field2 = name::space::one::SomeEnum::one;
    name::space::two::SomeEnum field3 = name::space::two::SomeEnum::ipsum;
    double field4 = -98765.4321;
    name::space::two::Foo_builder builder(field1, field2, field3, field4);
    
    std::vector<uint8_t> expected(12);
    auto p = expected.data();
    p = serialize(p, static_cast<std::int16_t>(12345));
    p = serialize(p, static_cast<std::uint8_t>(1));
    p = serialize(p, static_cast<std::uint8_t>(1));
    serialize(p, -98765.4321);
    
    auto result = builder.build();
    check_equal(result, expected);
}


int main(int argc, char* argv[])
{
    if(strcmp(argv[1], "view") == 0)
        test_view();
    if(strcmp(argv[1], "builder") == 0)
        test_builder();
}''')

    def test_view(self):
        exit_code, output = self.run_all(testargs=["view"])
        self.assertEqual(exit_code, 0)

    def test_builder(self):
        exit_code, output = self.run_all(testargs=["builder"])
        self.assertEqual(exit_code, 0)
