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
import re

import workspace_test_evaluate

from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    testOutputPath = os.path.join(dataBasePath, 'outputs')

    expectedJsonPath = os.path.abspath(os.path.join(dataBasePath, 'expected.json'))
    receivedJsonPath = os.path.abspath(os.path.join(dataBasePath, 'recieved.json'))

    outputJunitXmlPath = os.path.abspath(os.path.join(testOutputPath, 'test.junit.xml'))
    outputRefJunitXmlPath = os.path.abspath(os.path.join(dataBasePath, 'test_ref.junit.xml'))

    def setup_class(cls):
        ''' Setup any state specific to the execution of the given class (which usually contains tests). '''
        # create output folder
        BaseTestCaseCapture.createFolder(TestMain.testOutputPath)

    def callfunc(self, *args, **kwargs):
        workspace_test_evaluate.main(*args, **kwargs)

    def test_args_basic(self):
        ''' Tests some basic sets of args '''
        self.t_missingRequiredArgs([[]])
        self.t_missingRequiredArgs([['/some/random/path']])
        self.t_unrecognizedArgs([['/some/random/path', '-s', 'randomNonPositionalArg']])

    def test_noExceptionIfFails(self):
        ''' Tests if script does not raise exception when one of tests fails and parameter --exception_if_fail is set to False '''
        self.t_noException([[self.expectedJsonPath, self.receivedJsonPath, '-o', self.outputJunitXmlPath]])
        with open(self.outputJunitXmlPath, 'r') as f1, open(self.outputRefJunitXmlPath, 'r') as f2:
            for l1, l2 in zip(f1, f2):
                # remove timestamp because it is not static
                l1 = re.sub(r' timestamp="[^"]*"', '', l1)
                l2 = re.sub(r' timestamp="[^"]*"', '', l2)
                # remove time because it is not static
                l1 = re.sub(r' time="[^"]*"', '', l1)
                l2 = re.sub(r' time="[^"]*"', '', l2)
                assert l1 == l2

    def test_raiseExceptionIfFails(self):
        ''' Tests if script raises exception when one of tests fails and parameter --exception_if_fail is set to True '''
        self.t_raiseException(
            NameError,
            'FailedTestDetected',
            [[self.expectedJsonPath, self.receivedJsonPath, '-o', self.outputJunitXmlPath, '-e']])
