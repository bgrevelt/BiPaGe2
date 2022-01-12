from Model.semantic_analysis_unittests import SemanticAnalysisUnittests
import unittest
from build_model import build_model_test
from Model.ImportedFile import ImportedFile
from Model.Enumeration import Enumeration
from Model.Types.SignedInteger import SignedInteger
from Model.Types.UnsignedInteger import UnsignedInteger


class SemanticAnalysisImportsUnittests(SemanticAnalysisUnittests):
    # Use an enumeration from an imported file
    def test_external_enum(self):
        imports = [ImportedFile('import.bp', [], '', [
            Enumeration('ImportedEnum', UnsignedInteger(8, None), [('first', 0), ('second', 1)], None)])]
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
        imports = [ImportedFile('import.bp', [], '', [
            Enumeration('ImportedEnum2', UnsignedInteger(8, None), [('first', 0), ('second', 1)], None)])]
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
        imports = [ImportedFile('import.bp', [], '', [
            Enumeration('MyEnum', UnsignedInteger(8, None), [('first', 0), ('second', 1)], None)])]
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
            ImportedFile(
                path='import.bp',
                imports = [],
                namespace='ns',
                enumerations=[
                    Enumeration(
                        name='MyEnum',
                        base_type=UnsignedInteger(8, None),
                        enumerators=[
                            ('first', 0),
                            ('second', 1)
                        ],
                        token=None
                    )
                ]
            )
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
            ImportedFile(
                path='import.bp',
                imports=[],
                namespace='some.name.space',
                enumerations=[
                    Enumeration(
                        name='MyEnum',
                        base_type=UnsignedInteger(8, None),
                        enumerators=[
                            ('first', 0),
                            ('second', 1)
                        ],
                        token=None)
                    ]
                )
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
        imports = [ImportedFile('import.bp', [], '', [
            Enumeration('MyEnum', UnsignedInteger(8, None), [('first', 0), ('second', 1)], None)])]
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



