from build_model import build_model_test
from Model.Definition import Definition
from Model.Enumeration import Enumeration
from Model.types import UnsignedInteger
from Model.unittests.semantic_analysis_test_case import SemanticAnalysisUnitTestCase

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
            field2 : sMyEnum;
            field3 : float64;
        }
        ''', imports)
        # Didn't include the namespace so we should get an unknown type error
        self.checkErrors(errors, [(5, 21, "Reference \"sMyEnum\" cannot be resolved")])

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



