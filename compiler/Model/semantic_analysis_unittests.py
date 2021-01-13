import unittest
from .Builder import Builder
import random

class SemanticAnalysisUnittests(unittest.TestCase):
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

    def test_integer_size(self):
        # We create a type with a size in the range [1,99] to test if we get an error if the size is 1 or greater than
        # 64. We create a second type that will make the total size of the Datatype a multitude of 8 bits to prevent
        # additional errors. We make sure that one is in the range of numbers to test because we want to test that.
        sizes = [1] + random.sample(range(1, 100), 10)
        for n, size in enumerate(sizes):
            type = "uint" if n%2 == 1 else "int"
            other_size = 8-(size%8)
            if other_size <= 1:
                other_size += 8
            warnings, errors, _ = Builder().build(f'''
SomeDataType
{{
    field1 : {type}{size};
    field2 : {type}{other_size};
}}
''')
            if 2 <= size <= 64:
                self.checkErrors(errors, []) # no error
            elif size > 64:
                self.checkErrors(errors, [(4, 4, 'outside supported range'),
                                          (4, 4, 'cannot be captured in a type that is 64 bits or less in size')])
            else:
                self.checkErrors(errors, [(4, 4, 'outside supported range')])

    def test_non_standard_field_outside_of_capture_scope(self):
        # Non-standard types out of capture scope. Should yield errors.
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    f1 : int16;   
    f2 : int12; 
    f3 : int4;   
}''')
        self.checkErrors(errors, [(5, 4, 'Field f2 should be in a capture scope.'),
                                  (6, 4, 'Field f3 should be in a capture scope.')])

        # Same object only now with capture scope in place. Should not yield any errors.
        warnings, errors, _ = Builder().build('''
        SomeDataType
        {
            f1 : int16;   
            {
                f2 : int12; 
                f3 : int4;
            }   
        }''')
        self.checkErrors(errors, [])


    def test_capture_scope_too_large(self):
        # we currently don't support capture scopes larger than 64 bits.
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    {
        f1 : int6;   
        f2 : uint59; 
        f3 : int7;   
    }
}''')
        self.checkErrors(errors, [(4, 4, 'Larger than the maximum supported capture type')])

        warnings, errors, _ = Builder().build('''
        SomeDataType
        {
            {
                f1 : int6;   
                f2 : uint58;  
            }
        }''')
        self.checkErrors(errors, [])

    def test_capture_scope_size(self):
        # multitude of 8 bits, but not a standard type width
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    {
        f1 : int6;
        f2 : uint30;
        f3 : int4;   // Total size: 40 bits
    }
    f4 : int8;
    f5: u16;
}''')
        self.checkErrors(errors, [(4, 4, 'fields in capture scope (40 bits) is not a standard size')])  # no error

        # Standard type width. No errors
        warnings, errors, _ = Builder().build('''
        SomeDataType
        {
            {
                f1 : int6;
                f2 : uint22;
                f3 : int4;   // Total size: 32 bits
            }
        }''')
        self.checkErrors(errors, [])  # no error

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
        not_expected_errors = [e for e in errors if e not in matched_errors]
        msg = "unmatched expecteds:\n" + "\n".join(str(e) for e in not_matched_expectations)
        msg += "\nunmatched errors:\n" + "\n".join([str(e) for e in not_expected_errors])
        self.assertEqual(len(not_matched_expectations), 0, msg)

        if not allow_extra_errors:

            self.assertEqual(len(not_expected_errors), 0, msg)

