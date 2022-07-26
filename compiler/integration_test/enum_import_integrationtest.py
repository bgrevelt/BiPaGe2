import unittest
from compiler.integration_test.integrationtest import IntegrationTest


class ImportEnum(unittest.TestCase, IntegrationTest):

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
        ''', 'MyEnums.bp')

        self.write_bipage_file('''
        import "MyEnums.bp";
        Foo
        {
            field1 : s16;
            field2 : SomeEnum;
            field3 : SomeEnum;
            field4 : SomeEnum;
            field5 : SomeEnum;
            field6 : SomeEnum;
            field7 : f64;
        }
        ''')


        self.write_cmake_file()
        self.write_test_cpp_file('''
#include "enum_import_integrationtest_generated.h"
#include <iostream>
#include "../check.hpp"

void test_view()
{            
    std::uint8_t buffer[1024];
    auto p = buffer;
    p = serialize(p, static_cast<std::int16_t>(-635));
    p = serialize(p, static_cast<std::uint8_t>(1));
    p = serialize(p, static_cast<std::uint8_t>(2));
    p = serialize(p, static_cast<std::uint8_t>(5));
    p = serialize(p, static_cast<std::uint8_t>(9));
    p = serialize(p, static_cast<std::uint8_t>(255));
    p = serialize(p, -123.456);

    Foo_view parsed(buffer);

    check_equal(parsed.field1(), -635);
    check_equal(parsed.field2(), SomeEnum::one);
    check_equal(parsed.field3(), SomeEnum::two);
    check_equal(parsed.field4(), SomeEnum::five);
    check_equal(parsed.field5(), SomeEnum::nine);
    check_equal(parsed.field6(), SomeEnum::twofiftyfive);
    check_equal(parsed.field7(), -123.456);
    check_equal(parsed.size_in_bytes(), 15);
}

void test_builder()
{
    int16_t field1 = 12345;
    SomeEnum field2 = SomeEnum::one;
    SomeEnum field3 = SomeEnum::two;
    SomeEnum field4 = SomeEnum::five;
    SomeEnum field5 = SomeEnum::nine;
    SomeEnum field6 = SomeEnum::twofiftyfive;
    double field7 = -98765.4321;
    Foo_builder builder(field1, field2, field3, field4, field5, field6, field7);
    
    std::vector<uint8_t> expected(15);
    auto p = expected.data();
    p = serialize(p, static_cast<std::int16_t>(12345));
    p = serialize(p, static_cast<std::uint8_t>(1));
    p = serialize(p, static_cast<std::uint8_t>(2));
    p = serialize(p, static_cast<std::uint8_t>(5));
    p = serialize(p, static_cast<std::uint8_t>(9));
    p = serialize(p, static_cast<std::uint8_t>(255));
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
