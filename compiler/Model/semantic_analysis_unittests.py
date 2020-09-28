import unittest
from .Builder import Builder

class SemanticAnalysis_unittests(unittest.TestCase):
    def test_duplicate_field_name(self):
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    duplicate : int32;
    test : float64;
    duplicate : u8;
    test : s64;
}
        ''')
        self.checkErrors(errors, [(4,4, 'duplicate'),
                             (5,4, 'test'),
                             (6, 4, 'duplicate'),
                             (7, 4, 'test')])

    def test_duplicate_field_different_datatype(self):
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    duplicate : int32;
    test : float64;
}

SomeOtherDataType
{
    duplicate : int32;
    test : float64;
}
        ''')
        self.checkErrors(errors, [])

    def test_duplicate_datatype_name(self):
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    f1 : int32;
    f2 : float64;
    f3 : u8;
    f4 : s64;
}

SomeDataType
{
    f1 : int32;
    f2 : float64;
    f3 : u8;
    f4 : s64;
}''')
        self.checkErrors(errors, [(2, 0, 'SomeDataType'),
                                      (10, 0, 'SomeDataType')])

    def test_float_width(self):
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    f1 : float64;
    f2 : float16;
    f3 : float32;
}''')
        self.checkErrors(errors, [(5, 9, 'float16')], True)


    def checkErrors(self, errors, expected, allow_extra_errors = False):
        matched_errors = []
        matched_expected = []
        for ex in expected:
            line, column, contains = ex
            for error in errors:
                if error.line == line and error.column == column and contains in error.message:
                    matched_errors.append(error)
                    matched_expected.append(ex)
                    break

        not_matched_expectations = [e for e in expected if e not in matched_expected]
        self.assertEqual(len(not_matched_expectations), 0, "\n".join(not_matched_expectations))

        if not allow_extra_errors:
            not_expected_errors = [e for e in errors if e not in matched_errors]
            self.assertEqual(len(not_expected_errors), 0, "\n".join([str(e) for e in not_expected_errors]))

