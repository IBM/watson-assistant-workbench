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

import pytest

import wawCommons

from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    sourceJsonDict = {
        'notTargetKeyA': None,
        'notTargetKeyB': 'notToBeReplacedValue',
        'notTargetKeyC': 'targetKey',
        'notTargetKeyD': {
            'notTargetKeyDA': None,
            'notTargetKeyDB': 'notToBeReplacedValue',
            'notTargetKeyDC': 'targetKey',
            'notTargetKeyDD': {
                'notTargetKeyDDA': None,
                'notTargetKeyDDB': 'notToBeReplacedValue',
                'notTargetKeyDDC': 'targetKey',
                'targetKey': {},
                'notTargetKeyDDE': []
            },
            'notTargetKeyDE': [
                None,
                'targetKey',
                'notTargetKeyDEC',
                {},
                []
            ]
        },
        'targetKey': [
            None,
            'targetKey',
            'notTargetKeyEC',
            {
                'notTargetKeyEDA': None,
                'notTargetKeyEDB': 'notToBeReplacedValue',
                'notTargetKeyEDC': 'targetKey',
                'targetKey': {},
                'notTargetKeyEDE': []
            },
            [
                None,
                'targetKey',
                'notTargetKeyEEC',
                {},
                []
            ]
        ]
    }

    sourceJsonList = [
        None,
        'targetKey',
        'notTargetKeyC',
        {
            'notTargetKeyDA': None,
            'notTargetKeyDB': 'notToBeReplacedValue',
            'notTargetKeyDC': 'targetKey',
            'notTargetKeyDD': {
                'notTargetKeyDDA': None,
                'notTargetKeyDDB': 'notToBeReplacedValue',
                'notTargetKeyDDC': 'targetKey',
                'targetKey': {},
                'notTargetKeyDDE': []
            },
            'notTargetKeyDE': [
                None,
                'targetKey',
                'notTargetKeyDEC',
                {},
                []
            ]
        },
        [
            None,
            'targetKey',
            'notTargetKeyEC',
            {
                'notTargetKeyEDA': None,
                'notTargetKeyEDB': 'notToBeReplacedValue',
                'notTargetKeyEDC': 'targetKey',
                'targetKey': {},
                'notTargetKeyEDE': []
            },
            [
                None,
                'targetKey',
                'notTargetKeyEEC',
                {},
                []
            ]
        ]
    ]

    def test_sourceNull(self):
        ''' Tests if sourceJson is Null '''
        rJson, rReplacementNumber = wawCommons.replaceValue(None, 'targetKey', 'replacementJson')
        assert rReplacementNumber == 0
        assert rJson == None

    def test_keyNull(self):
        ''' Tests if targetKey is Null '''
        sourceJsonDict = dict(self.sourceJsonDict)
        rJson, rReplacementNumber = wawCommons.replaceValue(sourceJsonDict, None, 'replacementJson')
        assert rReplacementNumber == 0
        assert rJson == self.sourceJsonDict
        assert sourceJsonDict == self.sourceJsonDict

    def test_sourceString(self):
        ''' Tests if sourceJson is String '''
        rJson, rReplacementNumber = wawCommons.replaceValue('sourceJson', 'targetKey', 'replacementJson')
        assert rJson == 'sourceJson'
        assert rReplacementNumber == 0

    def test_noReplacementDict(self):
        ''' Tests if targetKey is not in sourceJson, dict '''
        sourceJsonDict = dict(self.sourceJsonDict)
        rJson, rReplacementNumber = wawCommons.replaceValue(sourceJsonDict, 'randomKey', 'replacementJson')
        assert rReplacementNumber == 0
        assert rJson == self.sourceJsonDict
        assert sourceJsonDict == self.sourceJsonDict

    def test_noReplacementList(self):
        ''' Tests if targetKey is not in sourceJson, list'''
        sourceJsonList = list(self.sourceJsonList)
        rJson, rReplacementNumber = wawCommons.replaceValue(sourceJsonList, 'randomKey', 'replacementJson')
        assert rReplacementNumber == 0
        assert rJson == self.sourceJsonList
        assert sourceJsonList == self.sourceJsonList

    @pytest.mark.parametrize('replacement', [None, 'replacementJson', {'replacementKey': 'replacementValue'}])
    def test_replacementDict(self, replacement):
        ''' Tests if value of targetKey is replaced by different object, dict '''
        sourceJsonDict = dict(self.sourceJsonDict)
        rJson, rReplacementNumber = wawCommons.replaceValue(sourceJsonDict, 'targetKey', replacement)
        assert rReplacementNumber == 2
        assert sourceJsonDict == self.sourceJsonDict
        assert rJson == {
            'notTargetKeyA': None,
            'notTargetKeyB': 'notToBeReplacedValue',
            'notTargetKeyC': 'targetKey',
            'notTargetKeyD': {
                'notTargetKeyDA': None,
                'notTargetKeyDB': 'notToBeReplacedValue',
                'notTargetKeyDC': 'targetKey',
                'notTargetKeyDD': {
                    'notTargetKeyDDA': None,
                    'notTargetKeyDDB': 'notToBeReplacedValue',
                    'notTargetKeyDDC': 'targetKey',
                    'targetKey': replacement,
                    'notTargetKeyDDE': []
                },
                'notTargetKeyDE': [
                    None,
                    'targetKey',
                    'notTargetKeyDEC',
                    {},
                    []
                ]
            },
            'targetKey': replacement
        }

    @pytest.mark.parametrize('replacement', [None, 'replacementJson', {'replacementKey': 'replacementValue'}])
    def test_replacementList(self, replacement):
        ''' Tests if value of targetKey is replaced by different object, list '''
        sourceJsonList = list(self.sourceJsonList)
        rJson, rReplacementNumber = wawCommons.replaceValue(sourceJsonList, 'targetKey', replacement)
        assert rReplacementNumber == 2
        assert sourceJsonList == self.sourceJsonList
        assert rJson == [
            None,
            'targetKey',
            'notTargetKeyC',
            {
                'notTargetKeyDA': None,
                'notTargetKeyDB': 'notToBeReplacedValue',
                'notTargetKeyDC': 'targetKey',
                'notTargetKeyDD': {
                    'notTargetKeyDDA': None,
                    'notTargetKeyDDB': 'notToBeReplacedValue',
                    'notTargetKeyDDC': 'targetKey',
                    'targetKey': replacement,
                    'notTargetKeyDDE': []
                },
                'notTargetKeyDE': [
                    None,
                    'targetKey',
                    'notTargetKeyDEC',
                    {},
                    []
                ]
            },
            [
                None,
                'targetKey',
                'notTargetKeyEC',
                {
                    'notTargetKeyEDA': None,
                    'notTargetKeyEDB': 'notToBeReplacedValue',
                    'notTargetKeyEDC': 'targetKey',
                    'targetKey': replacement,
                    'notTargetKeyEDE': []
                },
                [
                    None,
                    'targetKey',
                    'notTargetKeyEEC',
                    {},
                    []
                ]
            ]
        ]

    @pytest.mark.parametrize('replacement', [None, 'replacementJson', {'replacementKey': 'replacementValue'}])
    def test_replacementDictValue(self, replacement):
        ''' Tests if value of targetKey is replaced by different object, dict '''
        sourceJsonDict = dict(self.sourceJsonDict)
        rJson, rReplacementNumber = wawCommons.replaceValue(sourceJsonDict, 'targetKey', replacement, False)
        assert rReplacementNumber == 7
        assert sourceJsonDict == self.sourceJsonDict
        assert rJson == {
            'notTargetKeyA': None,
            'notTargetKeyB': 'notToBeReplacedValue',
            'notTargetKeyC': replacement,
            'notTargetKeyD': {
                'notTargetKeyDA': None,
                'notTargetKeyDB': 'notToBeReplacedValue',
                'notTargetKeyDC': replacement,
                'notTargetKeyDD': {
                    'notTargetKeyDDA': None,
                    'notTargetKeyDDB': 'notToBeReplacedValue',
                    'notTargetKeyDDC': replacement,
                    'targetKey': {},
                    'notTargetKeyDDE': []
                },
                'notTargetKeyDE': [
                    None,
                    replacement,
                    'notTargetKeyDEC',
                    {},
                    []
                ]
            },
            'targetKey': [
                None,
                replacement,
                'notTargetKeyEC',
                {
                    'notTargetKeyEDA': None,
                    'notTargetKeyEDB': 'notToBeReplacedValue',
                    'notTargetKeyEDC': replacement,
                    'targetKey': {},
                    'notTargetKeyEDE': []
                },
                [
                    None,
                    replacement,
                    'notTargetKeyEEC',
                    {},
                    []
                ]
            ]
        }

    @pytest.mark.parametrize('replacement', [None, 'replacementJson', {'replacementKey': 'replacementValue'}])
    def test_replacementListValue(self, replacement):
        ''' Tests if value of targetKey is replaced by different object, list '''
        sourceJsonList = list(self.sourceJsonList)
        rJson, rReplacementNumber = wawCommons.replaceValue(sourceJsonList, 'targetKey', replacement, False)
        assert rReplacementNumber == 7
        assert sourceJsonList == self.sourceJsonList
        assert rJson == [
            None,
            replacement,
            'notTargetKeyC',
            {
                'notTargetKeyDA': None,
                'notTargetKeyDB': 'notToBeReplacedValue',
                'notTargetKeyDC': replacement,
                'notTargetKeyDD': {
                    'notTargetKeyDDA': None,
                    'notTargetKeyDDB': 'notToBeReplacedValue',
                    'notTargetKeyDDC': replacement,
                    'targetKey': {},
                    'notTargetKeyDDE': []
                },
                'notTargetKeyDE': [
                    None,
                    replacement,
                    'notTargetKeyDEC',
                    {},
                    []
                ]
            },
            [
                None,
                replacement,
                'notTargetKeyEC',
                {
                    'notTargetKeyEDA': None,
                    'notTargetKeyEDB': 'notToBeReplacedValue',
                    'notTargetKeyEDC': replacement,
                    'targetKey': {},
                    'notTargetKeyEDE': []
                },
                [
                    None,
                    replacement,
                    'notTargetKeyEEC',
                    {},
                    []
                ]
            ]
        ]
