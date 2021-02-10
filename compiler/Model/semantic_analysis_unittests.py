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
        ''', "")
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
        ''', "")
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
}''', "")
        self.checkErrors(errors, [(2, 0, 'SomeDataType'),
                                      (10, 0, 'SomeDataType')])

    def test_float_width(self):
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    f1 : float64;
    f2 : float16;
    f3 : float32;
}''', "")
        self.checkErrors(errors, [(5, 9, 'float16')], True)

    def test_integer_size(self):
        # validate that non-valid integer sizes are reported
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    {
        field1 : uint1; // not allowed, a one bit integer does not make sense. Use a boolean.
        field2 : uint7;
    }
}
''', "")
        self.checkErrors(errors, [(5,17,'outside supported range')])

        # Maximum integer size is 64 bits
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    field1 : int128; // not allowed, too large.
}
''', "")
        self.checkErrors(errors, [(4,13,'outside supported range')])


    def test_non_standard_field_outside_of_capture_scope(self):
        # Non-standard types out of capture scope. Should yield errors.
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    f1 : int16;   
    f2 : int12; 
    f3 : int4;   
}''', "")
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
        }''', "")
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
}''', "")
        self.checkErrors(errors, [(4, 4, 'Larger than the maximum supported capture type')])

        warnings, errors, _ = Builder().build('''
        SomeDataType
        {
            {
                f1 : int6;   
                f2 : uint58;  
            }
        }''', "")
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
}''', "")
        self.checkErrors(errors, [(4, 4, 'fields in capture scope (40 bits) is not a standard size')])

        # Standard type width. No errors
        warnings, errors, _ = Builder().build('''
        SomeDataType
        {
            {
                f1 : int6;
                f2 : uint22;
                f3 : int4;   // Total size: 32 bits
            }
        }''', "")
        self.checkErrors(errors, [])  # no error

    def test_only_standard_in_capture_scope(self):
        warnings, errors, _ = Builder().build('''
SomeDataType
{
    {
        f1 : int8;
        f2 : u16;
        f3 : s32;   
    }
    f4 : int8;
}''', "")
        self.checkErrors(warnings, [(4, 4, 'Capture scope contains only standard types')])  # no error

    def test_empty_data_type(self):
        warnings, errors, _ = Builder().build('''
    SomeDataType
    {
        
    }''', "")
        self.checkErrors(errors, [(5, 4, '')])  # This should give an error because it doesn't conform to the grammar

    def test_one_empty_data_type(self):
        warnings, errors, _ = Builder().build('''
    SomeDataType
    {
        f1 : int32;
        f2 : float64;
        f3 : u8;
        f4 : s64;
    }
    
    ThisOneIsEmpty
    {
    
    }''', "")
        self.checkErrors(errors, [(13, 4, '')])  # This should give an error because it doesn't conform to the grammar

    def test_empty_data_type_only_comments(self):
        warnings, errors, _ = Builder().build('''
    SomeDataType
    {
        // Just
        // Some
        /* comments in here */
    }''', "")
        self.checkErrors(errors, [(7, 4, '')])  # This should give an error because it doesn't conform to the grammar

    def test_padding_only_type(self):
        warnings, errors, _ = Builder().build('''
    SomeDataType
    {
        int32;
        float64;
        u8;
        s64;
    }''', "")
        self.checkErrors(warnings, [(2, 4, 'SomeDataType has no non-padding fields')])

    def test_invalid_enumerand_value(self):
        warnings, errors, _ = Builder().build('''
    SomeEnum : uint8
    {
        val1 = 0,
        val2 = 255,
        val3 = 256
    }''', "")
        self.checkErrors(errors, [(2, 4, 'val3 in enumeration SomeEnum has a value that is outside of the supported range of the underlying type')])

        warnings, errors, _ = Builder().build('''
    SomeEnum : int16
    {
        aap = -32768,
        noot = 32767,
        mies = 32768
    }''', "")
        self.checkErrors(errors, [(2, 4,
                                   'mies in enumeration SomeEnum has a value that is outside of the supported range of the underlying type')])

    def test_duplicated_enumerand_value(self):
        warnings, errors, _ = Builder().build('''
    SomeEnum : uint8
    {
        val1 = 0,
        val2 = 35,
        val3 = 35
    }''', "")
        self.checkErrors(errors, [(2, 4, 'Same value (35) used by mulitple enumerands in enumeration SomeEnum')],allow_extra_errors=True)

    def test_duplicated_enumerand_name(self):
        warnings, errors, _ = Builder().build('''
    SomeEnum : int64
    {
        val1 = 0,
        val2 = 1,
        val3 = 2,
        val4 = 3,
        val5 = 4,
        val6 = 5,
        val7 = 6,
        val8 = 7,
        val9 = 8,
        val1 = 9
    }''', "")
        self.checkErrors(errors, [(2, 4, 'Duplicated enumerand val1 in SomeEnum')],allow_extra_errors=True)

    def test_non_existing_enumeration(self):
        warnings, errors, _ = Builder().build('''
    SomeEnum : uint64
    {
        val1 = 0,
        val2 = 1,
        val3 = 2,
        val4 = 3,
        val5 = 4,
        val6 = 5,
        val7 = 6,
        val8 = 7,
        val9 = 8,
        val10 = 9
    }
    
    SomeDataType
    {
        field1 : uint8;
        field2 : SomeOtherEnum;
        field3 : float64;
    }
    
    ''', "")
        self.checkErrors(errors, [(19, 17, 'Reference "SomeOtherEnum" cannot be resolved')],allow_extra_errors=True)

    def test_name_duplication(self):
        warnings, errors, _ = Builder().build('''
            Foo : uint64
            {
                val1 = 0,
                val2 = 1,
                val3 = 2
            }

            Foo
            {
                field1 : uint8;
                field2 : Foo;
                field3 : float64;
            }

            ''', "")
        self.checkErrors(errors, [
            (2, 12, 'Name Foo used for multiple type definitions'),
            (9, 12, 'Name Foo used for multiple type definitions')])


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

