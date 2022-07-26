from compiler.build_model import build_model_test, build_model_from_file
from compiler.Model.Definition import Definition
from compiler.Model.Enumeration import Enumeration
from compiler.Model.types import UnsignedInteger
from compiler.Model.DataType import DataType
from compiler.Model.Field import Field
from compiler.Model.unittests.semantic_analysis_test_case import SemanticAnalysisUnitTestCase
import os

class SemanticAnalysisImportsUnittests(SemanticAnalysisUnitTestCase):
    # Use an enumeration from an imported file
    def test_external_enum(self):
        imports = [
                      Definition(
                          name='import',
                          endianness='little',
                          namespace=[],
                          imports=[],
                          datatypes=[],
                          enumerations=[
                              Enumeration(
                                  name='ImportedEnum',
                                  base_type=UnsignedInteger(8, None),
                                  enumerators=[
                                      ('first', 0),
                                      ('second', 1)
                                  ],
                                  token=None)
                          ],
                          token=None )
                    ]

        text = '''
        Foo
        {
            field1 : uint8;
            field2 : ImportedEnum;
            field3 : float64;
        }
        '''
        warnings, errors, _ = build_model_test(text, imports)
        self.checkErrors(errors, [])  # Enum exists in import so we should not get any errors

    def test_missing_external_enum(self):
        imports = [
                      Definition(
                          name='import',
                          endianness='little',
                          namespace=[],
                          imports=[],
                          datatypes=[],
                          enumerations=[
                              Enumeration(
                                  name='ImportedEnum2',
                                  base_type=UnsignedInteger(8, None),
                                  enumerators=[
                                      ('first', 0),
                                      ('second', 1)
                                  ],
                                  token=None)
                          ],
                          token=None )
                    ]
        text = '''
        Foo
        {
            field1 : uint8;
            field2 : ImportedEnum;
            field3 : float64;
        }
        '''
        warnings, errors, _ = build_model_test(text, imports)
        self.checkErrors(errors, [(5, 21,
                                   'Reference "ImportedEnum" cannot be resolved')])  # Enum does not exists in import so we should get an errors

    def test_duplicated_type_name(self):
        imports = [
            Definition(
                name='import',
                endianness='little',
                namespace=[],
                imports=[],
                datatypes=[],
                enumerations=[
                    Enumeration(
                        name='MyEnum',
                        base_type=UnsignedInteger(8, None),
                        enumerators=[
                            ('first', 0),
                            ('second', 1)
                        ],
                        token=None)
                ],
                token=None)
        ]
        text = '''
        MyEnum : s32
        {
           enumerator_one = 1,
           enumerator_two = 2,
           enumerator_three = 3
        }
        
        Foo
        {
            field1 : uint8;
            field2 : MyEnum;
            field3 : float64;
        }
        '''
        warnings, errors, _ = build_model_test(text, imports)
        self.checkErrors(errors, [(2,8,"Mutiple defintions found for MyEnum")])

    def test_duplicated_type_name_in_namespace(self):
        imports = [
            Definition(
                name='import',
                endianness='little',
                namespace=['ns'],
                imports=[],
                datatypes=[],
                enumerations=[
                    Enumeration(
                        name='MyEnum',
                        base_type=UnsignedInteger(8, None),
                        enumerators=[
                            ('first', 0),
                            ('second', 1)
                        ],
                        token=None)
                ],
                token=None)
        ]
        text = '''
        MyEnum : s32
        {
           enumerator_one = 1,
           enumerator_two = 2,
           enumerator_three = 3
        }

        Foo
        {
            field1 : uint8;
            field2 : MyEnum;
            field3 : float64;
        }
        '''
        warnings, errors, _ = build_model_test(text, imports)
        # Two enums with the same name but they're in different name spaces, so no errors.
        self.checkErrors(errors, [])

    def test_imported_enum_in_namespace(self):
        imports = [
            Definition(
                name='import',
                endianness='little',
                namespace=['some','name','space'],
                imports=[],
                datatypes=[],
                enumerations=[
                    Enumeration(
                        name='MyEnum',
                        base_type=UnsignedInteger(8, None),
                        enumerators=[
                            ('first', 0),
                            ('second', 1)
                        ],
                        token=None)
                ],
                token=None)
        ]

        warnings, errors, _ = build_model_test('''
        Foo
        {
            field1 : uint8;
            field2 : some.name.space.MyEnum;
            field3 : float64;
        }
        ''', imports)
        # Properly used the namespace. Should not lead to errors
        self.checkErrors(errors, [])

        warnings, errors, _ = build_model_test('''
        namespace my.own.name.space;
        Foo
        {
            field1 : uint8;
            field2 : some.name.space.MyEnum;
            field3 : float64;
        }
        ''', imports)
        # Same as before only now the datatype is in a namespace as well. That shouldn't matter
        self.checkErrors(errors, [])

        warnings, errors, _ = build_model_test('''
        Foo
        {
            field1 : uint8;
            field2 : MyEnum;
            field3 : float64;
        }
        ''', imports)
        # Didn't include the namespace so we should get an unknown type error
        self.checkErrors(errors, [(5, 21, "Reference \"MyEnum\" cannot be resolved")])

    def test_imported_enumerator(self):
        imports = [
            Definition(
                name='import',
                endianness='little',
                namespace=[],
                imports=[],
                datatypes=[],
                enumerations=[
                    Enumeration(
                        name='MyEnum',
                        base_type=UnsignedInteger(8, None),
                        enumerators=[
                            ('first', 0),
                            ('second', 1)
                        ],
                        token=None)
                ],
                token=None)
        ]
        text = '''
        Foo
        {
            field1 : MyEnum;
            field2 : f64[field1==MyEnum.first?1:0];
            field3 : float64;
        }
        '''
        warnings, errors, _ = build_model_test(text, imports)
        self.checkErrors(errors, [])

    # Verify that errors are reported in the right file
    def test_reporting_in_right_file(self):
        files = {
            'ext_enum.bp': '''
            ThatOneEnumeration : int8
            {
                catastrophe = -3,
                fatal = -2,
                error = -1,
                OK = 0,
                awesome = 1
            }''',
            'ext_datatype1.bp' : '''
            MyExternalDataType1
            {
                collection_size: s16;
                collection: u8[collection_size];  // <-- Using a sized int for collection size should raise a warning in this file
            }''',
            'ext_datatype2.bp': '''
            MyExternalDataType2
            {
                field1: f64;
                {                   // <-- Capture scope that only contains standard size fields should raise a warning here
                    field2:u32;
                    field3:s8;
                    field4:s16;
                    field5:u8;
                }
                field6: u16;
            }''',
            'ext_datatype3.bp': '''
            MyExternalDataType3
            {
                field1: f64;
                field2: u8[0];      // <-- Empty collection should raise a warning here
                field3: u16;
            }''',
            'ext_datatype4.bp': '''
            MyExternalDataType4    // <-- Data type with only padding fields
            {
                f64;
                u8;      
                u16;
            }''',
            'root.bp': '''
            import "ext_datatype1.bp";
            import "ext_datatype2.bp";
            import "ext_datatype3.bp";
            import "ext_datatype4.bp";
            import "ext_enum.bp";
            MyRootDataType
            {
                size : s8;
                ThatOneEnumeration; // <-- Using an enumeration for padding should raise a warning in this file
                col: u32[10];         
            }'''
        }

        for path, content in files.items():
            with open(path, 'w') as f:
                f.write(content)

        # Do things
        warnings, errors, _ = build_model_from_file('root.bp')

        self.checkErrors(errors, [])

        self.checkErrors(warnings, [
            ('ext_datatype1.bp', 5, 16, 'Collection sized by signed integer'),
            ('ext_datatype2.bp', 5, 16, 'Capture scope contains only standard types'),
            ('ext_datatype3.bp', 5, 16, 'Collection with zero elements'),
            ('ext_datatype4.bp', 2, 12, 'MyExternalDataType4 has no non-padding fields'),
            ('root.bp', 10, 16, 'Using enumeration as padding'),

        ])

        for path in files:
           os.remove(path)

    def test_imported_datatype_in_namespace(self):
        imports = [
            Definition(
                name='import',
                endianness='little',
                namespace=['some','name','space'],
                imports=[],
                datatypes=[
                    DataType(
                        identifier='Bar',
                        capture_scopes = [],
                        fields = [
                            Field(
                                name='field1',
                                type=UnsignedInteger(8,None),
                                static_offset=0,
                                dynamic_offset=None,
                                token=None)
                        ],
                        token=None)
                ],
                enumerations=[],
                token=None)
        ]

        warnings, errors, _ = build_model_test('''
        Foo
        {
            field1 : uint8;
            field2 : some.name.space.Bar;
            field3 : float64;
        }
        ''', imports)
        # Properly used the namespace. Should not lead to errors
        self.checkErrors(errors, [])

        warnings, errors, _ = build_model_test('''
        namespace my.own.name.space;
        Foo
        {
            field1 : uint8;
            field2 : some.name.space.Bar;
            field3 : float64;
        }
        ''', imports)
        # Same as before only now the datatype is in a namespace as well. That shouldn't matter
        self.checkErrors(errors, [])

        warnings, errors, _ = build_model_test('''
        Foo
        {
            field1 : uint8;
            field2 : Bar;
            field3 : float64;
        }
        ''', imports)
        # Didn't include the namespace so we should get an unknown type error
        self.checkErrors(errors, [(5, 21, "Reference \"Bar\" cannot be resolved")])


