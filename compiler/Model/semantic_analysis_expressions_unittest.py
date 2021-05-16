from Model.semantic_analysis_unittests import SemanticAnalysisUnittests
from build_model import build_model_test


class SemanticAnalysisExpressionsUnittests(SemanticAnalysisUnittests):
    def test_simple_arithmetic_expression(self):
        text = '''
        Foo
        {
            field : uint8[(2^4/4)+1-2*3];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    def test_simple_arithmetic_expression_invalid_size(self):
        text = '''
        Foo
        {
            field : uint8[5/2];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [
            (2,8,'Datatypes should be a multiple of eight in size')
        ])

    # division can lead to non-integer results. We should always issue a warning
    def test_division_collection_size(self):
        text = '''
        Foo
        {
            field1 : u32;
            field2 : u8;
            field3 : uint8[field1/field2];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    # Negative power can lead to non-integer result, we should issue a warning
    def test_signed_power_collection_size(self):
        text = '''
        Foo
        {
            field1 : u32;
            field2 : s8;
            field3 : uint8[field1^field2];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    # expressions that return (can) return a signed value should lead to a warning
    def test_arithmetic_signed_collection_size(self):
        text = '''
        Foo
        {
            field1 : u32;
            field2 : s16;
            field3 : uint8[field1+field2];
            field4 : uint8[field1*field2];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    def test_reference_ternary_expressions(self):
        text = '''
        Foo
        {
            field0 : u32;
            field1 : uint8[field0 < 3 ? 10 : 20];
            field2 : uint8[field0 <=3 ? 10 : 20];
            field3 : uint8[field0 > 3 ? 10 : 20];
            field4 : uint8[field0 >=3 ? 10 : 20];
            field5 : uint8[field0 ==3 ? 10 : 20];
            field6 : uint8[field0 !=3 ? 10 : 20];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    # Comparing a signed value to a negative value should raise a warning
    # Both for literals and references
    def test_reference_ternary_expressions(self):
        text = '''
        Foo
        {
            fielda : u32;
            fieldb : s32;
            field1 : uint8[field0 <  -3 ? 10 : 20];
            field2 : uint8[field0 <= -3 ? 10 : 20];
            field3 : uint8[field0 >  -3 ? 10 : 20];
            field4 : uint8[field0 >= -3 ? 10 : 20];
            field5 : uint8[field0 == -3 ? 10 : 20];
            field6 : uint8[field0 != -3 ? 10 : 20];
            field7 : uint8[field0 <  fieldb ? 10 : 20];
            field8 : uint8[field0 <= fieldb ? 10 : 20];
            field9 : uint8[field0 >  fieldb ? 10 : 20];
            field10: uint8[field0 >= fieldb ? 10 : 20];
            field11: uint8[field0 == fieldb ? 10 : 20];
            field12: uint8[field0 != fieldb ? 10 : 20];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    def test_ternary_different_types(self):
        text = '''
        Foo
        {
            {
                field1 : flag;
                field2 : u7;
            } 
            field3: uint8[field1 ? field1 : field2];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    # Ternary can return signed value. This should lead to a warning just like when we directly use a signed value
    def test_ternary_potential_signed(self):
        text = '''
        Foo
        {
            {
                field1 : flag;
                field2 : u3;
                field3 : s4;
            } 
            field4: uint8[field1 ? field2 : field3];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    # Arithmetic operations only support integer operands
    # Arithmetic operations on floating point values may be mathematically valid, but I don't think we'll need them to
    # size collections.
    def test_arithmetic_non_integer(self):
        text = '''
        SomeEnum : u16
        {
          v1 = 1,
          v2 = 2
        }
        
        Foo
        {
            {
                field1 : flag;
                u7;
            } 
            field2 : u32;
            field3 : f64;
            field4 : SomeEnum;
            
            collection1: uint8[field1 + field2]; // Can't add a bool to an int
            collection2: uint8[field4 * field2]; // Can't multiply an enum with an int
            collection3: uint8[field1 / field2]; // Can't divide a bool by an int
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [
            (18,31,"Left hand operand (field1) does not resolve to integer or float"),
            (19,31,"Left hand operand (field4) does not resolve to integer or float"),
            (20,31,"Left hand operand (field1) does not resolve to integer or float")
        ])

    def test_non_int_collection_size(self):
        text = '''
        Foo
        {
            field1 : uint32;
            field2 : float64;
            collection1 : uint8[field2]; // Can't use a float to size a collection
            collection2 : uint8[field1 + field2]; // So you can't
            collection3 : uint8[field2 - field1]; // use an expression
            collection4 : uint8[field1 * field2]; // that resolves to
            collection5 : uint8[field2 / field1]; // a float
            collection6 : uint8[field1 ^ field2]; // either
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [
            (6,12,"Only integer fields can be used to size a collection. Not Float"),
            (7, 12, "Only integer fields can be used to size a collection. Not Float"),
            (8, 12, "Only integer fields can be used to size a collection. Not Float"),
            (9, 12, "Only integer fields can be used to size a collection. Not Float"),
            (10, 12, "Only integer fields can be used to size a collection. Not Float"),
            (11, 12, "Only integer fields can be used to size a collection. Not Float")
        ])

    # We don't support comparing to float
    def test_comparison_on_float_expressions(self):
        text = '''
        Foo
        {
            fielda : f32;
            fieldb : f64;
            field1 : uint8[fielda <  0 ? 10 : 20];
            field2 : uint8[fielda <= 0 ? 10 : 20];
            field3 : uint8[fielda >  0 ? 10 : 20];
            field4 : uint8[fielda >= 0 ? 10 : 20];
            field5 : uint8[fielda == 0 ? 10 : 20];
            field6 : uint8[fielda != 0 ? 10 : 20];
            field7 : uint8[fieldb <  0 ? 10 : 20];
            field8 : uint8[fieldb <= 0 ? 10 : 20];
            field9 : uint8[fieldb >  0 ? 10 : 20];
            field10: uint8[fieldb >= 0 ? 10 : 20];
            field11: uint8[fieldb == 0 ? 10 : 20];
            field12: uint8[fieldb != 0 ? 10 : 20];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    def test_valid_int_reference(self):
        text = '''
        Foo
        {
            field1 : uint32;
            field2 : uint8[field1];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    def test_valid_flag_reference(self):
        text = '''
        Foo
        {
            {
                field1 : flag;
                field2 : s7;
            }
            field3 : uint8[field1 ? field2 : 0];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    def test_invalid_flag_reference(self):
        text = '''
        Foo
        {
            field1 : u16;
            field2 : f32;
            field3 : uint8[field1 ? field2 : 0];
            field4 : uint8[field2 ? 8 : 0];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    def test_valid_enum_reference(self):
        text = '''
        SomeEnum : u8
        {
            val1 = 1,
            val2 = 2,
            val3 = 3
        }
        
        Foo
        {
            field1 : SomeEnum;
            field2 : uint8[field1 == SomeEnum.val2 ? 20 : 40];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    # We don't allow treating an enum like an integer
    def test_valid_enum_reference(self):
        text = '''
        SomeEnum : u8
        {
            val1 = 1,
            val2 = 2,
            val3 = 3
        }

        Foo
        {
            field1 : SomeEnum;
            field2 : uint8[field1 == 2 ? 20 : 40];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    def test_enum_reference_non_existent_enumerand(self):
        text = '''
        SomeEnum : u8
        {
            val1 = 1,
            val2 = 2,
            val3 = 3
        }

        Foo
        {
            field1 : SomeEnum;
            field2 : uint8[field1 == SomeEnum.val4 ? 20 : 40];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    def test_enumerator_reference_for_non_enum_field(self):
        text = '''
        SomeEnum : u8
        {
            val1 = 1,
            val2 = 2,
            val3 = 3
        }

        Foo
        {
            field1 : SomeEnum;
            field2 : s64;
            field3 : uint8[field2 == SomeEnum.val2 ? 20 : 40];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])

    # We don't support using enumerator value as if it were an integer
    def test_enumerator_value_used_as_collection_size(self):
        text = '''
        SomeEnum : u8
        {
            val1 = 1,
            val2 = 2,
            val3 = 3
        }

        Foo
        {
            field : uint8[SomeEnum.val2];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [])