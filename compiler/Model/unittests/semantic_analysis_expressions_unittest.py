from Model.unittests.semantic_analysis_test_case import SemanticAnalysisUnitTestCase
from build_model import build_model_test


class SemanticAnalysisExpressionsUnittests(SemanticAnalysisUnitTestCase):
    def test_simple_arithmetic_expression(self):
        text = '''
        Foo
        {
            field : uint8[(16/4)+1-2*3];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [
            (4,12,'Negative number of elements in collection')
        ])

    def test_simple_arithmetic_expression_invalid_size(self):
        text = '''
        Foo
        {
            field : uint8[5/2];
            field2 : uint8[5/2]; // Needed so the complete datatype adds up to a complete number of bytes. Otherwise that error is thrown first.
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [
            (4,12,'Invalid collection size')
        ], allow_extra_errors=True)

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
        self.checkErrors(warnings, [
            (6,27,'Division operator (field1 / field2) may have in non-integer result')
        ])

    # expressions that (can) return a signed value should lead to a warning
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
        self.checkErrors(warnings, [
            (6, 12, "Expression sizing collection resolves to signed type."),
            (7, 12, "Expression sizing collection resolves to signed type.")
        ])

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

    # Comparing an unsigned value to a negative value should raise a warning
    # Both for literals and references
    def test_reference_ternary_expressions2(self):
        text = '''
        Foo
        {
            fielda : u32;
            field1 : uint8[fielda <  -3 ? 10 : 20];
            field2 : uint8[fielda <= -3 ? 10 : 20];
            field3 : uint8[fielda >  -3 ? 10 : 20];
            field4 : uint8[fielda >= -3 ? 10 : 20];
            field5 : uint8[fielda == -3 ? 10 : 20];
            field6 : uint8[fielda != -3 ? 10 : 20];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [
            (5, 27, "Comparing unsigned value to a negative literal"),
            (6, 27, "Comparing unsigned value to a negative literal"),
            (7, 27, "Comparing unsigned value to a negative literal"),
            (8, 27, "Comparing unsigned value to a negative literal"),
            (9, 27, "Comparing unsigned value to a negative literal"),
            (10, 27, "Comparing unsigned value to a negative literal")
        ])

    # Ternary expressions should return the same type for both clauses
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
        self.checkErrors(errors, [
            (8,26,'Different types for true (Flag) and false (UnsignedInteger) clause')
        ])

    # Ternary can return signed value. This should lead to a warning just like when we directly use a signed value
    # Disabled this test for now because we don't allow ternary to return different types. Signed and Unsigned integers
    # are considered different types. Leaving this in because we may at some point choose to allow mixing of signedness
    # def test_ternary_potential_signed(self):
    #     text = '''
    #     Foo
    #     {
    #         {
    #             field1 : flag;
    #             field2 : u3;
    #             field3 : s4;
    #         }
    #         field4: uint8[field1 ? field2 : field3];
    #     }
    #     '''
    #     warnings, errors, _ = build_model_test(text, "")
    #     self.checkErrors(errors, [
    #         (9,12,'Collection sized by signed integer. If the field has a negative value this will lead to runtime errors.')
    #     ])

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
            collection5 : uint8[field2 / field1]; // a float either
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [
            (6,12,"Only integer fields can be used to size a collection. Not Float"),
            (7, 12, "Only integer fields can be used to size a collection. Not Float"),
            (8, 12, "Only integer fields can be used to size a collection. Not Float"),
            (9, 12, "Only integer fields can be used to size a collection. Not Float"),
            (10, 12, "Only integer fields can be used to size a collection. Not Float")
        ])

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
        self.checkErrors(warnings, [
            (8,12,'Expression sizing collection resolves to signed type. This could lead to runtime trouble if the actual value is negative.')
        ])

    def test_invalid_flag_reference(self):
        text = '''
        Foo
        {
            field1 : u16;
            field2 : f32;
            field3 : uint8[field1 ? 5 : 0];
            field4 : uint8[field2 ? 8 : 0];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [
            (6,27,"UnsignedInteger not allowed as ternary condition"),
            (7, 27, "Float not allowed as ternary condition")
        ])

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

    def test_different_enum_reference(self):
        text = '''
        SomeEnum : u8
        {
            val1 = 1,
            val2 = 2,
            val3 = 3
        }
        
        SomeOtherEnum : u8
        {
            val1 = 1,
            val2 = 2,
            val3 = 3
        }

        Foo
        {
            field1 : SomeEnum;
            field2 : uint8[field1 == SomeOtherEnum.val2 ? 20 : 40];
        }
        '''
        warnings, errors, _ = build_model_test(text, "")
        self.checkErrors(errors, [
            (19, 27, "Can't compare SomeEnum to SomeOtherEnum")
        ])

    # We don't allow treating an enum like an integer
    def test_constant_against_enum_reference(self):
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
        self.checkErrors(errors, [
            (12,27,"Can't compare SomeEnum to UnsignedInteger")
        ])

    def test_enum_reference_non_existent_enumerator(self):
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
        self.checkErrors(errors, [
            (12,37,'Reference "SomeEnum.val4" cannot be resolved')
        ])

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
        self.checkErrors(errors, [
            (13,27,"Can't compare SignedInteger to SomeEnum")
        ])

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
        self.checkErrors(errors, [
            (11,12,"Only integer fields can be used to size a collection. Not SomeEnum")
        ])