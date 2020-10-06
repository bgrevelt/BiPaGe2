import unittest
from .Beautifier import Beautifier

class BeautifierUnittest(unittest.TestCase):
    def test_class_no_indent(self):
        input = \
'''
class Foo
{
public:
int Bar()
{
return 0;
}
};'''
        expected = \
'''
class Foo
{
public:
    int Bar()
    {
        return 0;
    }
};'''
        beatifier = Beautifier()
        self.assertEqual(beatifier.beautify(input), expected)

    def test_class_with_indent(self):
        input = \
'''
class Foo
{
    public:
        int Bar()
        {
                return 0;
        }
                };'''
        expected = \
'''
class Foo
{
public:
    int Bar()
    {
        return 0;
    }
};'''
        beatifier = Beautifier()
        self.assertEqual(beatifier.beautify(input), expected)

    def test_class_namespace(self):
        input = \
'''
namespace ns1
{
namespace ns2
{
class Foo
{
public:
int Bar()
{
return 0;
}
};
}
}'''
        expected = \
'''
namespace ns1
{
    namespace ns2
    {
        class Foo
        {
        public:
            int Bar()
            {
                return 0;
            }
        };
    }
}'''
        beatifier = Beautifier()
        self.assertEqual(beatifier.beautify(input), expected)


    def test_multi_line_parameter(self):
        input = \
'''
class Foo
{
public:
Foo(
int param1,
int param2)
{
}
};'''
        expected = \
'''
class Foo
{
public:
    Foo(
        int param1,
        int param2)
    {
    }
};'''
        beatifier = Beautifier()
        self.assertEqual(beatifier.beautify(input), expected)