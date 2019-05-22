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

import json
import os
import re

import functions_test_evaluate

from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    testOutputPath = os.path.join(dataBasePath, 'outputs')

    outputCommonPath = os.path.abspath(os.path.join(testOutputPath, 'common.out'))
    noJsonPath = os.path.abspath(os.path.join(dataBasePath, 'no.json'))
    emptyDictJsonPath = os.path.abspath(os.path.join(dataBasePath, 'empty_dict.json'))
    testSingleInvalidOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_invalid.out.json'))
    testSingleAllInFileOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file.out.json'))
    testSingleAllInFileFailedOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file_failed.out.json'))
    testSinglePayloadsOutOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out.out.json'))
    testSinglePayloadsOutNoJsonOutputExpectedOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out_no_json_output_expected.out.json'))
    testSinglePayloadsOutNoJsonOutputReturnedOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out_no_json_output_returned.out.json'))
    testSinglePayloadsOutNonExistingOutputExpectedOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out_non_existing_output_expected.out.json'))
    testSinglePayloadsOutNonExistingOutputReturnedOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out_non_existing_output_returned.out.json'))
    testSingleAllInFileBadTypeOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file_bad_type.out.json'))
    testMultiOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_multi.out.json'))
    testMultiJUnitXmlOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_multi_junitxml.out.json'))
    testMultiJUnitXmlRefEvalJUnitXmlPath = os.path.abspath(os.path.join(dataBasePath, 'test_multi_junitxml_ref.eval.junit.xml'))

    def setup_class(cls):
        ''' Setup any state specific to the execution of the given class (which usually contains tests). '''
        # create output folder
        BaseTestCaseCapture.createFolder(TestMain.testOutputPath)

    def callfunc(self, *args, **kwargs):
        functions_test_evaluate.main(*args, **kwargs)

    def test_args_basic(self):
        ''' Tests some basic sets of args '''
        self.t_missingRequiredArgs([[]])
        self.t_missingRequiredArgs([['/some/random/path']])
        self.t_unrecognizedArgs([['/some/random/path', '-s', 'randomNonPositionalArg']])

    def test_nonExistentFileInput(self):
        ''' Tests if the input file does not exist '''
        testArgs = ['/some/random/path', '/some/random/path']
        self.t_exitCodeAndLogMessage(
            1, # exit code
            "CRITICAL Cannot open test output file '/some/random/path'", # critical message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_nonExistentFileOutput(self):
        ''' Tests if the output file does not exist '''
        testArgs = [self.noJsonPath, '/some/random/path']
        self.t_exitCodeAndLogMessage(
            1, # exit code
            "CRITICAL Cannot open evaluation output file '/some/random/path'", # critical message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_invalidJsonInput(self):
        ''' Tests if the input file contains invalid json '''
        testArgs = [self.noJsonPath, self.outputCommonPath]
        self.t_exitCodeAndLogMessage(
            1, # exit code
            'CRITICAL Cannot decode json from test output file', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_nonArrayJsonInput(self):
        ''' Tests if the input file contains non array json '''
        testArgs = [self.emptyDictJsonPath, self.outputCommonPath]
        self.t_exitCodeAndLogMessage(
            1, # exit code
            'CRITICAL Test output json is not array!', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSingleInvalid(self):
        ''' Tests if the input file contains test that is not dictionary '''
        testArgs = [self.testSingleInvalidOutJsonPath, self.outputCommonPath]
        self.t_noExceptionAndLogMessage(
            'ERROR    Input test array element 0 is not dictionary. Each test has to be dictionary, please see doc!', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSingleAllInFile(self):
        ''' Tests if the single test where input and expected output is specified
         in file (all other params are given from command line) '''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.basename(self.testSingleAllInFileOutJsonPath).split('.')[0] + '.eval.json'))
        testArgs = [self.testSingleAllInFileOutJsonPath, outputFilePath]
        self.t_noException([testArgs])
        with open(outputFilePath, 'r') as outputFile:
            outputJson = json.load(outputFile)
            assert outputJson == [
                {
                    "input": {
                        "message": "test message"
                    },
                    "outputReturned": {
                        "message": "test message"
                    },
                    "outputExpected": {
                        "message": "test message"
                    },
                    "result": 0
                }
            ]

    def test_testSingleAllInFileFailed(self):
        ''' Tests if the single test where input and expected output is specified
         in file (all other params are given from command line) and returned output differs '''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.basename(self.testSingleAllInFileFailedOutJsonPath).split('.')[0] + '.eval.json'))
        testArgs = [self.testSingleAllInFileFailedOutJsonPath, outputFilePath]
        self.t_noException([testArgs])
        with open(outputFilePath, 'r') as outputFile:
            outputJson = json.load(outputFile)
            assert outputJson == [
                {
                    "input": {
                        "message": "test message"
                    },
                    "outputReturned": {
                        "message": "test message"
                    },
                    "outputExpected": {
                        "message": "bad expected message"
                    },
                    "diff": {
                        "values_changed": {
                            "root['message']": {
                                "new_value": "test message",
                                "old_value": "bad expected message"
                            }
                        }
                    },
                    "result": 1
                }
            ]

    def test_testSinglePayloadsOut(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file (all other params are given from command line) '''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.basename(self.testSinglePayloadsOutOutJsonPath).split('.')[0] + '.eval.json'))
        testArgs = [self.testSinglePayloadsOutOutJsonPath, outputFilePath]
        self.t_noException([testArgs])
        with open(outputFilePath, 'r') as outputFile:
            outputJson = json.load(outputFile)
            assert outputJson == [
                {
                    "input": "@test_single_payload.json",
                    "outputReturned": {
                        "message": "test message"
                    },
                    "outputExpected": {
                        "message": "test message"
                    },
                    "result": 0
                }
            ]

    def test_testSinglePayloadsOutNonExistingOutputExpected(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file but input path is wrong (all other params are given from command line) '''
        testArgs = [self.testSinglePayloadsOutNonExistingOutputExpectedOutJsonPath, self.outputCommonPath]
        self.t_noExceptionAndLogMessage(
            "ERROR    Cannot open expected output payload from file '/some/random/path'", # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSinglePayloadsOutNoJsonOutputExpected(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file but input is invalid json
         (all other params are given from command line) '''
        testArgs = [self.testSinglePayloadsOutNoJsonOutputExpectedOutJsonPath, self.outputCommonPath]
        self.t_noExceptionAndLogMessage(
            'ERROR    Cannot decode json from expected output payload from file', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSinglePayloadsOutNonExistingOutputReturned(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file but expected output path
         is wrong (all other params are given from command line) '''
        testArgs = [self.testSinglePayloadsOutNonExistingOutputReturnedOutJsonPath, self.outputCommonPath]
        self.t_noExceptionAndLogMessage(
            "ERROR    Cannot open returned output payload from file '/some/random/path'", # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSinglePayloadsOutNoJsonOutputReturned(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file but expected output
         is invalid json (all other params are given from command line) '''
        testArgs = [self.testSinglePayloadsOutNoJsonOutputReturnedOutJsonPath, self.outputCommonPath]
        self.t_noExceptionAndLogMessage(
            'ERROR    Cannot decode json from returned output payload from file', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSingleAllInFileBadType(self):
        ''' Tests if bad test type was provided '''
        testArgs = [self.testSingleAllInFileBadTypeOutJsonPath, self.outputCommonPath]
        self.t_noExceptionAndLogMessage(
            'ERROR    Unknown test type: BAD TYPE', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testMulti(self):
        ''' Tests if there are multi tests in input file '''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.basename(self.testMultiOutJsonPath).split('.')[0] + '.eval.json'))
        testArgs = [self.testMultiOutJsonPath, outputFilePath]
        self.t_noException([testArgs])
        with open(outputFilePath, 'r') as outputFile:
            outputJson = json.load(outputFile)
            assert outputJson == [
                {
                    "input": "@test_single_payload.json",
                    "outputReturned": {
                        "message": "test message"
                    },
                    "outputExpected": {
                        "message": "test message"
                    },
                    "result": 0
                },
                {
                    "input": {
                        "message": "test message 2"
                    },
                    "outputReturned": {
                        "message": "test message 2"
                    },
                    "outputExpected": {
                        "message": "test message 2"
                    },
                    "result": 0
                }
            ]

    def test_nonExistentJUnitXmlFileOutput(self):
        ''' Tests if the JUnit XML output file does not exist '''
        testArgs = [self.noJsonPath, self.noJsonPath, '-j', '/some/random/path']
        self.t_exitCodeAndLogMessage(
            1, # exit code
            "CRITICAL Cannot open evaluation JUnit XML output file '/some/random/path'", # critical message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testMultiJUnitXml(self):
        ''' Tests if junit xml is generated correctly '''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.basename(self.testMultiJUnitXmlOutJsonPath).split('.')[0] + '.eval.json'))
        outputJUnitXmlFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.basename(self.testMultiJUnitXmlOutJsonPath).split('.')[0] + '.eval.junit.xml'))

        testArgs = [self.testMultiJUnitXmlOutJsonPath, outputFilePath, '-j', outputJUnitXmlFilePath]
        self.t_noException([testArgs])
        with open(self.testMultiJUnitXmlRefEvalJUnitXmlPath, 'r') as f1, open(outputJUnitXmlFilePath, 'r') as f2:
            for l1, l2 in zip(f1, f2):
                # remove timestamp because it is not static
                l1 = re.sub(r' timestamp="[^"]*"', '', l1)
                l2 = re.sub(r' timestamp="[^"]*"', '', l2)
                # remove absolute path because it is not static
                l1 = re.sub(r' from file [^ ]*no.json', '', l1)
                l2 = re.sub(r' from file [^ ]*no.json', '', l2)
                assert l1 == l2
