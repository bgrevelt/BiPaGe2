from Model.semantic_analysis_unittests import SemanticAnalysisUnittests
import unittest
from build_model import build_model_test
from Model.ImportedFile import ImportedFile
from Model.Enumeration import Enumeration
from Model.Types.Integer import Integer

'''
Simple case: Have an enum in bp file 1, use in in bp file 2
Different namespaces. Same as the simple case, but both files use different namespaces
Same name enums in different namespaces. Have an enum with the same name in 2 files with different namespaces. Import both files and use both enumerations.
Have a Datatype within a namespace use an enumeration in another files that doesn't have a namespace. This validates that we also search for things in the 'default namespace' even when we're in a namespace.
Semantic analysis
(fully qualified) names across all imported files should be unique
'''


class SemanticAnalysisImportsUnittests(SemanticAnalysisUnittests):
    # Use an enumeration from an imported file
    def test_external_enum(self):
        imports = [ImportedFile('import.bp', [], '', [
            Enumeration('ImportedEnum', Integer(8, False, None), [('first', 0), ('second', 1)], None)])]
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
            Enumeration('ImportedEnum2', Integer(8, False, None), [('first', 0), ('second', 1)], None)])]
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
            Enumeration('MyEnum', Integer(8, False, None), [('first', 0), ('second', 1)], None)])]
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

    def test_imported_enum_in_namespace(self):
        imports = [
            ImportedFile(
                path='import.bp',
                imports=[],
                namespace='some.name.space',
                enumerations=[
                    Enumeration(
                        name='MyEnum',
                        base_type=Integer(8, False, None),
                        enumerators=[
                            ('first', 0),
                            ('second', 1)
                        ],
                        token=None)
                    ]
                )
            ]
        text = '''
        Foo
        {
            field1 : uint8;
            field2 : some.name.space.MyEnum;
            field3 : float64;
        }
        '''
        warnings, errors, _ = build_model_test(text, imports)
        # Properly used the namespace. Should not lead to errors
        self.checkErrors(errors, [])

