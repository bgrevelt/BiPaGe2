import unittest
from build_model import build_model_from_text, build_model_test
from Model.ImportedFile import ImportedFile
from Model.Enumeration import Enumeration
from Model.Types.Integer import Integer

class SemanticAnalysisUnittests(unittest.TestCase):
    def test_duplicate_field_name(self):
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
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
        self.checkErrors(errors, [(2, 0, 'SomeDataType')])

    def test_float_width(self):
        warnings, errors, _ = build_model_from_text('''
SomeDataType
{
    f1 : float64;
    f2 : float16;
    f3 : float32;
}''', "")
        self.checkErrors(errors, [(5, 9, 'float16')], True)

    def test_integer_size(self):
        # validate that non-valid integer sizes are reported
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
SomeDataType
{
    field1 : int128; // not allowed, too large.
}
''', "")
        self.checkErrors(errors, [(4,13,'outside supported range')])


    def test_non_standard_field_outside_of_capture_scope(self):
        # Non-standard types out of capture scope. Should yield errors.
        warnings, errors, _ = build_model_from_text('''
SomeDataType
{
    f1 : int16;   
    f2 : int12; 
    f3 : int4;   
}''', "")
        self.checkErrors(errors, [(5, 4, 'Field f2 should be in a capture scope.'),
                                  (6, 4, 'Field f3 should be in a capture scope.')])

        # Same object only now with capture scope in place. Should not yield any errors.
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
SomeDataType
{
    {
        f1 : int6;   
        f2 : uint59; 
        f3 : int7;   
    }
}''', "")
        self.checkErrors(errors, [(4, 4, 'Larger than the maximum supported capture type')])

        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
    SomeDataType
    {
        
    }''', "")
        self.checkErrors(errors, [(5, 4, '')])  # This should give an error because it doesn't conform to the grammar

    def test_one_empty_data_type(self):
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
    SomeDataType
    {
        // Just
        // Some
        /* comments in here */
    }''', "")
        self.checkErrors(errors, [(7, 4, '')])  # This should give an error because it doesn't conform to the grammar

    def test_padding_only_type(self):
        warnings, errors, _ = build_model_from_text('''
    SomeDataType
    {
        int32;
        float64;
        u8;
        s64;
    }''', "")
        self.checkErrors(warnings, [(2, 4, 'SomeDataType has no non-padding fields')])

    def test_invalid_enumerand_value(self):
        warnings, errors, _ = build_model_from_text('''
    SomeEnum : uint8
    {
        val1 = 0,
        val2 = 255,
        val3 = 256
    }''', "")
        self.checkErrors(errors, [(6, 15, 'val3 in enumeration SomeEnum has a value that is outside of the supported range of the underlying type')])

        warnings, errors, _ = build_model_from_text('''
    SomeEnum : int16
    {
        aap = -32768,
        noot = 32767,
        mies = 32768
    }''', "")
        self.checkErrors(errors, [(6, 15,
                                   'mies in enumeration SomeEnum has a value that is outside of the supported range of the underlying type')])

    def test_duplicated_enumerand_value(self):
        warnings, errors, _ = build_model_from_text('''
    SomeEnum : uint8
    {
        val1 = 0,
        val2 = 35,
        val3 = 35
    }''', "")
        self.checkErrors(errors, [(5, 15, 'Same value (35) used by mulitple enumerands in enumeration SomeEnum')],allow_extra_errors=True)

    def test_duplicated_enumerand_name(self):
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
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
        warnings, errors, _ = build_model_from_text('''
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

        # A little dodgy. We know the warning will be thrown in the datatype and not the enum because of how SA iterates
        # the types, but now it looks like that's a requirement. Ideally we'd have some 'or' operation, but this is good
        # enough for nows
        self.checkErrors(errors, [
            (9, 12, 'Mutiple defintions found for Foo')])

    def test_enumerator_value_type(self):
        warnings, errors, _ = build_model_from_text('''
    SomeEnum : uint8
    {
        val1 = 0,
        val2 = 3+5,
        val3 = 3-5,
        val4 = 3*5,
        val5 = 3/5,
        val6 = (3),
        val7 = 3<5,
        val8 = 3<=5,
        val9 = 3>5,
        val10 = 3>=5,
        val11 = 3==5,
        valx = 35
    }''', "")
        self.checkErrors(errors, [
            (5, 15, 'Only number literals are allowed for enumerator values. Not AddOperator'),
            (6, 15, 'Only number literals are allowed for enumerator values. Not SubtractOperator'),
            (7, 15, 'Only number literals are allowed for enumerator values. Not MultiplyOperator'),
            (8, 15, 'Only number literals are allowed for enumerator values. Not DivisionOperator'),
            (10,15, 'Only number literals are allowed for enumerator values. Not LessThanOperator'),
            (11,15, 'Only number literals are allowed for enumerator values. Not LessThanEqualOperator'),
            (12,15, 'Only number literals are allowed for enumerator values. Not GreaterThanOperator'),
            (13,16, 'Only number literals are allowed for enumerator values. Not GreaterThanEqualOperator'),
            (14,16, 'Only number literals are allowed for enumerator values. Not EqualsOperator')
        ])

    def test_valid_collection(self):
        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            field1 : uint8;
            field2 : int32[8];
            field3 : float64;
        }

            ''', "")
        self.checkErrors(warnings, [])
        self.checkErrors(errors, [])

        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            field1 : uint8;
            field2 : int8 { one = 1, two=2, eight = 8}[8];
            field3 : float64;
        }

            ''', "")
        self.checkErrors(warnings, [])
        self.checkErrors(errors, [])

        warnings, errors, _ = build_model_from_text('''
        MyEnum: s32
        {
            one = 1, 
            two=2, 
            eight = 8
        }
        Foo
        {
            field1 : uint8;
            field2 : MyEnum[8];
            field3 : float64;
        }

            ''', "")
        self.checkErrors(warnings, [])
        self.checkErrors(errors, [])

    def test_zero_sized_collection(self):
        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            field1 : uint8;
            field2 : int32[0];
            field3 : float64;
        }

            ''', "")
        self.checkErrors(warnings, [
            (5, 12, 'Collection with zero elements')])

    def test_negative_sized_collection(self):
        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            field1 : uint8;
            field2 : int32[-1];
            field3 : float64;
        }

            ''', "")
        self.checkErrors(errors, [
            (5, 12, 'Negative number of elements in collection')])

    def test_non_standard_size_collection(self):
        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            field1 : uint8;
            field2 : int4[4];
            field3 : float64;
        }

            ''', "")
        self.checkErrors(errors, [
            (5, 12, 'Non-standard (4) sized types not supported in collection')])

        warnings, errors, _ = build_model_from_text('''
        MyEnum : u4
        {
            foo = 1,
            bar = 2
        }
    
        Foo
        {
            field1 : uint8;
            field2 : MyEnum[4];
            field3 : float64;
        }

                    ''', "")
        self.checkErrors(errors, [
            (11, 12, 'Non-standard (4) sized types not supported in collection')])

    def test_collection_in_capture_scope(self):
        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            field1 : uint8;
            {
                field2 : uint6;
                field3 : int8[2];
                field4 : int10;
            }
            field5 : float64;
        }

            ''', "")
        self.checkErrors(errors, [
            (7, 16, 'Collections inside a capture scope are not supported')])

    def test_collection_size_with_enum(self):
        warnings, errors, _ = build_model_from_text('''
        MyEnum : u8
        {
            a = 1,
            b = 2,
            c = 3
        }
        
        Foo
        {
            field1 : uint8[MyEnum];
        }''', "")
        self.checkErrors(errors, [
            (11,12, 'Only integer fields can be used to size a collection. Not MyEnum')
        ])

    def test_type_reference_is_field(self):
        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            field1 : u32;
            field2 : field1;
        }''', '')
        self.checkErrors(errors, [
            (5, 12, "Reference to Field is not a valid field type")])

    def test_collection_sized_by_non_existent_field(self):
        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            field1 : u32;
            field2 : u16[field3];
        }''', '')
        self.checkErrors(errors, [
            (5, 25, 'Reference "field3" cannot be resolved')])

    def test_collection_sized_by_non_int_field(self):
        warnings, errors, _ = build_model_from_text('''
        MyEnum : u7
        {
           a = 1,
           b = 2
        }
        Foo
        {
            field1 : f32;
            field2 : f64;
            {
                field3: MyEnum;
                field4: flag;
            }
            field5 : u8[4];
            
            collection1 : u8[field1]; // Collection sized by float32
            collection2 : u8[field2]; // Collection sized by float64
            collection3 : u8[field3]; // Collection sized by enumeration
            collection4 : u8[field4]; // Collection sized by Flag
            collection5 : u8[field5]; // Collection sized by other collection
        }''', '')
        self.checkErrors(errors, [
            (17, 12, "Only integer fields can be used to size a collection. Not Float."),
            (18, 12, "Only integer fields can be used to size a collection. Not Float."),
            (19, 12, "Only integer fields can be used to size a collection. Not MyEnum."),
            (20, 12, "Only integer fields can be used to size a collection. Not Flag."),
            (21, 12, "Only integer fields can be used to size a collection. Not Collection.")
        ])

    def test_collection_sized_by_signed_integer(self):
        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            field1 : s32;
            field2 : u16[field1];
        }''', '')
        self.checkErrors(warnings, [
            (5, 12, 'Collection sized by signed integer')])

    def test_padding_enum(self):
        warnings, errors, _ = build_model_from_text('''
        Foo
        {
            f1: u8;
            u8 {foo = 1, bar = 2};
            f2: f64;
        }''', '')
        self.checkErrors(warnings, [
            (5, 12, 'Using enumeration as padding. Is this really what you want?')])

        warnings, errors, _ = build_model_from_text('''
        MyEnum : u32
        {
            one = 1,
            two = 2,
            three = 3
        }
        
        Foo
        {
            f1: u8;
            MyEnum;
            f2: f64;
        }''', '')
        self.checkErrors(warnings, [
            (12, 12, 'Using enumeration as padding. Is this really what you want?')])

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

