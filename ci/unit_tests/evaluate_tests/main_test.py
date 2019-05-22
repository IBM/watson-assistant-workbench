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

import os

import evaluate_tests

from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    testOutputPath = os.path.join(dataBasePath, 'outputs')

    expectedJsonPath = os.path.abspath(os.path.join(dataBasePath, 'expected.json'))
    receivedJsonPath = os.path.abspath(os.path.join(dataBasePath, 'recieved.json'))

    outputJunitXmlPath = os.path.abspath(os.path.join(testOutputPath, 'test.junit.xml'))

    def setup_class(cls):
        ''' Setup any state specific to the execution of the given class (which usually contains tests). '''
        # create output folder
        BaseTestCaseCapture.createFolder(TestMain.testOutputPath)

    def callfunc(self, *args, **kwargs):
        evaluate_tests.main(*args, **kwargs)

    def test_args_basic(self):
        ''' Tests some basic sets of args '''
        self.t_missingRequiredArgs([[]])
        self.t_missingRequiredArgs([['/some/random/path']])
        self.t_unrecognizedArgs([['/some/random/path', '-s', 'randomNonPositionalArg']])

    def test_noExceptionIfFails(self):
        ''' Tests if script does not raise exception when one of tests fails and parameter --exception_if_fail is set to False '''
        self.t_noException([[self.expectedJsonPath, self.receivedJsonPath, '-o', self.outputJunitXmlPath]])

    def test_raiseExceptionIfFails(self):
        ''' Tests if script raises exception when one of tests fails and parameter --exception_if_fail is set to True '''
        self.t_raiseException(
            NameError,
            'FailedTestDetected',
            [[self.expectedJsonPath, self.receivedJsonPath, '-o', self.outputJunitXmlPath, '-e']])
