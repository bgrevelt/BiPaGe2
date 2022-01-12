import unittest

class SemanticAnalysisUnitTestCase(unittest.TestCase):
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