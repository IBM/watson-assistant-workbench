"""
Copyright 2019 IBM Corporation
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os, pytest, json

import compare_dialogs
from .. import unit_utils

class TestMain(unit_utils.BaseTestCaseCapture):

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

    def test_args(self):
        ''' Tests some basic sets of args '''
        self.tTooFewArgs([])
        self.tTooFewArgs(['/some/random/path'])
        self.tUnrecognizedArgs(['/some/random/path', '-s', 'randomNonPositionalArg'])

    def test_nonExistentFileFirst(self):
        ''' Tests if the first file does not exist '''
        self.tExitCodeAndErrMessage(
            1, # exit code
            'Input dialog json \'/some/random/path\' does not exist.', # error message substring
            [
                '/some/random/path',
                ''
            ] # params (*args, **kwargs)
        )

    def test_nonExistentFileSecond(self):
        ''' Tests if the second file does not exist '''
        self.tExitCodeAndErrMessage(
            1, # exit code
            'Output dialog json \'/some/random/path\' does not exist.', # error message substring
            [
                self.noJsonPath,
                '/some/random/path'
            ] # params (*args, **kwargs)
        )

    def test_invalidJsonFirst(self):
        ''' Tests if the first file contains invalid json '''
        self.tRaiseError(
            ValueError, # exeption
            'No JSON object could be decoded', # error message substring
            [
                self.noJsonPath,
                self.emptyDictJsonPath,
            ] # params (*args, **kwargs)
        )

    def test_invalidJsonSecond(self):
        ''' Tests if the second file contains invalid json '''
        self.tRaiseError(
            ValueError, # exeption
            'No JSON object could be decoded', # error message substring
            [
                self.emptyDictJsonPath,
                self.noJsonPath,
            ] # params (*args, **kwargs)
        )

    def test_compareBasicNullNull(self):
        ''' Tests if basic jsons are same - null, null '''
        self.tExitCode(0, [self.nullJsonPath, self.nullJsonPath])

    def test_compareBasicValueValue(self):
        ''' Tests if basic jsons are same - value, value '''
        self.tExitCode(0, [self.valueJsonPath, self.valueJsonPath])

    def test_compareBasicEmptyDictEmptyDict(self):
        ''' Tests if basic jsons are same - empty dict, empty dict'''
        self.tExitCode(0, [self.emptyDictJsonPath, self.emptyDictJsonPath])

    def test_compareBasicEmptyListEmptyList(self):
        ''' Tests if basic jsons are same - empty list, empty list'''
        self.tExitCode(0, [self.emptyListJsonPath, self.emptyListJsonPath])

    def test_compareBasicNullValue(self):
        ''' Tests if basic jsons are different - null, value and value, null '''
        self.tExitCode(1, [self.nullJsonPath, self.valueJsonPath])
        self.tExitCode(1, [self.valueJsonPath, self.nullJsonPath])

    def test_compareBasicNullEmptyDict(self):
        ''' Tests if basic jsons are different - null, empty dict and empty dict, null '''
        self.tExitCode(1, [self.nullJsonPath, self.emptyDictJsonPath])
        self.tExitCode(1, [self.emptyDictJsonPath, self.nullJsonPath])

    def test_compareBasicNullEmptyList(self):
        ''' Tests if basic jsons are different - null, empty list and empty list, null '''
        self.tExitCode(1, [self.nullJsonPath, self.emptyListJsonPath])
        self.tExitCode(1, [self.emptyListJsonPath, self.nullJsonPath])

    def test_compareBasicValueEmptyDict(self):
        ''' Tests if basic jsons are different - value, empty dict and empty dict, value '''
        self.tExitCode(1, [self.valueJsonPath, self.emptyDictJsonPath])
        self.tExitCode(1, [self.emptyDictJsonPath, self.valueJsonPath])

    def test_compareBasicValueEmptyList(self):
        ''' Tests if basic jsons are different - value, empty list and empty list, value '''
        self.tExitCode(1, [self.valueJsonPath, self.emptyListJsonPath])
        self.tExitCode(1, [self.emptyListJsonPath, self.valueJsonPath])

    def test_compareBasicEmptyDictEmptyList(self):
        ''' Tests if basic jsons are different - empty dict, empty list and empty list, empty dict '''
        self.tExitCode(1, [self.emptyDictJsonPath, self.emptyListJsonPath])
        self.tExitCode(1, [self.emptyListJsonPath, self.emptyDictJsonPath])

    def test_compareComplexSorted(self):
        ''' Tests if complex sorted jsons are same '''
        self.tExitCode(0, [self.complexDictJsonPath, self.complexDictJsonPath])

    def test_compareComplexUnsorted(self):
        ''' Tests if complex unsorted jsons are same '''
        self.tExitCode(0, [self.complexDictJsonPath, self.complexDictUnsortedJsonPath])
        self.tExitCode(0, [self.complexDictUnsortedJsonPath, self.complexDictJsonPath])

    def test_compareComplexDifferentEmpty(self):
        ''' Tests if complex jsons are different - empty ([] != {}) '''
        self.tExitCode(1, [self.complexDictJsonPath, self.complexDictDifferentEmptyJsonPath])
        self.tExitCode(1, [self.complexDictDifferentEmptyJsonPath, self.complexDictJsonPath])

    def test_compareComplexDifferentKey(self):
        ''' Tests if complex jsons are different - key '''
        self.tExitCode(1, [self.complexDictJsonPath, self.complexDictDifferentKeyJsonPath])
        self.tExitCode(1, [self.complexDictDifferentKeyJsonPath, self.complexDictJsonPath])

    def test_compareComplexDifferentValue(self):
        ''' Tests if complex jsons are different - value '''
        self.tExitCode(1, [self.complexDictJsonPath, self.complexDictDifferentValueJsonPath])
        self.tExitCode(1, [self.complexDictDifferentValueJsonPath, self.complexDictJsonPath])

    def test_compareComplexDifferentSub(self):
        ''' Tests if complex json and its subjson are different '''
        self.tExitCode(1, [self.complexDictJsonPath, self.complexDictSubJsonPath])
        self.tExitCode(1, [self.complexDictSubJsonPath, self.complexDictJsonPath])

