
import os, pytest, json

import compare_dialogs
from .. import unit_utils

class TestMain(unit_utils.TestCaseCapture):

    dataBasePath = './ci/unit_tests/compare_dialogs/compare_dialogs_data/'

    complexDictDifferentEmptyJsonPath = os.path.abspath(os.path.join(dataBasePath, 'complex_dict_different_empty.json'))
    complexDictDifferentKeyJsonPath = os.path.abspath(os.path.join(dataBasePath, 'complex_dict_different_key.json'))
    complexDictDifferentValueJsonPath = os.path.abspath(os.path.join(dataBasePath, 'complex_dict_different_value.json'))
    complexDictJsonPath = os.path.abspath(os.path.join(dataBasePath, 'complex_dict.json'))
    complexDictSubJsonPath = os.path.abspath(os.path.join(dataBasePath, 'complex_dict_sub.json'))
    complexDictUnsortedJsonPath = os.path.abspath(os.path.join(dataBasePath, 'complex_dict_unsorted.json'))
    emptyDictJsonPath = os.path.abspath(os.path.join(dataBasePath, 'empty_dict.json'))
    emptyListJsonPath = os.path.abspath(os.path.join(dataBasePath, 'empty_list.json'))
    noJsonPath = os.path.abspath(os.path.join(dataBasePath, 'no.json'))
    nullJsonPath = os.path.abspath(os.path.join(dataBasePath, 'null.json'))
    valueJsonPath = os.path.abspath(os.path.join(dataBasePath, 'value.json'))

    def callfunc(self, *args, **kwargs):
        compare_dialogs.main(*args, **kwargs)

    ''' Tests some basic sets of args '''
    def test_args(self):
        self.tTooFewArgs([])
        self.tTooFewArgs(['/some/random/path'])
        self.tUnrecognizedArgs(['/some/random/path', '-s', 'randomNonPositionalArg'])

    ''' Tests if the first file does not exist '''
    def test_nonExistentFileFirst(self):
        self.tExitCodeAndErrMessage(
            1, # exit code
            'Input dialog json \'/some/random/path\' does not exist.', # error message substring
            [
                '/some/random/path',
                ''
            ] # params (*args, **kwargs)
        )

    ''' Tests if the second file does not exist '''
    def test_nonExistentFileSecond(self):
        self.tExitCodeAndErrMessage(
            1, # exit code
            'Output dialog json \'/some/random/path\' does not exist.', # error message substring
            [
                self.noJsonPath,
                '/some/random/path'
            ] # params (*args, **kwargs)
        )

    ''' Tests if the first file contains invalid json '''
    def test_invalidJsonFirst(self):
        self.tRaiseError(
            ValueError, # exeption
            'No JSON object could be decoded', # error message substring
            [
                self.noJsonPath,
                self.emptyDictJsonPath,
            ] # params (*args, **kwargs)
        )

    ''' Tests if the second file contains invalid json '''
    def test_invalidJsonSecond(self):
        self.tRaiseError(
            ValueError, # exeption
            'No JSON object could be decoded', # error message substring
            [
                self.emptyDictJsonPath,
                self.noJsonPath,
            ] # params (*args, **kwargs)
        )

    ''' Tests if basic jsons are same - null, null '''
    def test_compareBasicNullNull(self):
        self.tExitCode(0, [self.nullJsonPath, self.nullJsonPath])

    ''' Tests if basic jsons are same - value, value '''
    def test_compareBasicValueValue(self):
        self.tExitCode(0, [self.valueJsonPath, self.valueJsonPath])

    ''' Tests if basic jsons are same - empty dict, empty dict'''
    def test_compareBasicEmptyDictEmptyDict(self):
        self.tExitCode(0, [self.emptyDictJsonPath, self.emptyDictJsonPath])

    ''' Tests if basic jsons are same - empty list, empty list'''
    def test_compareBasicEmptyListEmptyList(self):
        self.tExitCode(0, [self.emptyListJsonPath, self.emptyListJsonPath])

    ''' Tests if basic jsons are different - null, value and value, null '''
    def test_compareBasicNullValue(self):
        self.tExitCode(1, [self.nullJsonPath, self.valueJsonPath])
        self.tExitCode(1, [self.valueJsonPath, self.nullJsonPath])

    ''' Tests if basic jsons are different - null, empty dict and empty dict, null '''
    def test_compareBasicNullEmptyDict(self):
        self.tExitCode(1, [self.nullJsonPath, self.emptyDictJsonPath])
        self.tExitCode(1, [self.emptyDictJsonPath, self.nullJsonPath])

    ''' Tests if basic jsons are different - null, empty list and empty list, null '''
    def test_compareBasicNullEmptyList(self):
        self.tExitCode(1, [self.nullJsonPath, self.emptyListJsonPath])
        self.tExitCode(1, [self.emptyListJsonPath, self.nullJsonPath])

    ''' Tests if basic jsons are different - value, empty dict and empty dict, value '''
    def test_compareBasicValueEmptyDict(self):
        self.tExitCode(1, [self.valueJsonPath, self.emptyDictJsonPath])
        self.tExitCode(1, [self.emptyDictJsonPath, self.valueJsonPath])

    ''' Tests if basic jsons are different - value, empty list and empty list, value '''
    def test_compareBasicValueEmptyList(self):
        self.tExitCode(1, [self.valueJsonPath, self.emptyListJsonPath])
        self.tExitCode(1, [self.emptyListJsonPath, self.valueJsonPath])

    ''' Tests if basic jsons are different - empty dict, empty list and empty list, empty dict '''
    def test_compareBasicEmptyDictEmptyList(self):
        self.tExitCode(1, [self.emptyDictJsonPath, self.emptyListJsonPath])
        self.tExitCode(1, [self.emptyListJsonPath, self.emptyDictJsonPath])

    ''' Tests if complex sorted jsons are same '''
    def test_compareComplexSorted(self):
        self.tExitCode(0, [self.complexDictJsonPath, self.complexDictJsonPath])

    ''' Tests if complex unsorted jsons are same '''
    def test_compareComplexUnsorted(self):
        self.tExitCode(0, [self.complexDictJsonPath, self.complexDictUnsortedJsonPath])
        self.tExitCode(0, [self.complexDictUnsortedJsonPath, self.complexDictJsonPath])

    ''' Tests if complex jsons are different - empty ([] != {}) '''
    def test_compareComplexDifferentEmpty(self):
        self.tExitCode(1, [self.complexDictJsonPath, self.complexDictDifferentEmptyJsonPath])
        self.tExitCode(1, [self.complexDictDifferentEmptyJsonPath, self.complexDictJsonPath])

    ''' Tests if complex jsons are different - key '''
    def test_compareComplexDifferentKey(self):
        self.tExitCode(1, [self.complexDictJsonPath, self.complexDictDifferentKeyJsonPath])
        self.tExitCode(1, [self.complexDictDifferentKeyJsonPath, self.complexDictJsonPath])

    ''' Tests if complex jsons are different - value '''
    def test_compareComplexDifferentValue(self):
        self.tExitCode(1, [self.complexDictJsonPath, self.complexDictDifferentValueJsonPath])
        self.tExitCode(1, [self.complexDictDifferentValueJsonPath, self.complexDictJsonPath])

    ''' Tests if complex json and its subjson are different '''
    def test_compareComplexDifferentSub(self):
        self.tExitCode(1, [self.complexDictJsonPath, self.complexDictSubJsonPath])
        self.tExitCode(1, [self.complexDictSubJsonPath, self.complexDictJsonPath])

