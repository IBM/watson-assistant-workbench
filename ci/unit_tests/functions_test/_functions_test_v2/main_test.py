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

import pytest

import functions_test

from ....test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    testOutputPath = os.path.join(dataBasePath, 'outputs')

    outputCommonPath = os.path.abspath(os.path.join(testOutputPath, 'common.out'))
    noJsonPath = os.path.abspath(os.path.join(dataBasePath, 'no.json'))
    emptyDictJsonPath = os.path.abspath(os.path.join(dataBasePath, 'empty_dict.json'))
    testSingleInvalidJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_invalid.json'))
    testSingleAllInFileJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file.json'))
    testSingleAllInFileReplaceJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file_replace.json'))
    testSingleAllInFileReplacePackageJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file_replace_package.json'))
    testSingleAllInFileFailedJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file_failed.json'))
    testSinglePayloadsOutJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out.json'))
    testSinglePayloadsOutNoJsonInputJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out_no_json_input.json'))
    testSinglePayloadsOutNoJsonOutputJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out_no_json_output.json'))
    testSinglePayloadsOutNonExistingInputJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out_non_existing_input.json'))
    testSinglePayloadsOutNonExistingOutputJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_payloads_out_non_existing_output.json'))
    testSingleAllInFileBadTypeJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file_bad_type.json'))
    testSingleAllInFileOverridePackageJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file_override_package.json'))
    testSingleAllInFileOverrideFunctionJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file_override_function.json'))
    testMultiJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_multi.json'))

    def setup_class(cls):
        ''' Setup any state specific to the execution of the given class (which usually contains tests). '''
        BaseTestCaseCapture.checkEnvironmentVariables(['CLOUD_FUNCTIONS_USERNAME', 'CLOUD_FUNCTIONS_PASSWORD', 'CLOUD_FUNCTIONS_URL'])
        cls.cloudFunctionsUsername = os.environ.get('CLOUD_FUNCTIONS_USERNAME')
        cls.cloudFunctionsPassword = os.environ.get('CLOUD_FUNCTIONS_PASSWORD')
        cls.cloudFunctionsUrl = os.environ.get('CLOUD_FUNCTIONS_URL')
        cls.cloudFunctionsNamespace = 'whisk.system'
        cls.cloudFunctionsPackage = 'utils'
        cls.cloudFunctionsFunction = 'echo'
        cls.functionsTestArgs = [
            '--cloudfunctions_url', cls.cloudFunctionsUrl,
            '--cloudfunctions_namespace', cls.cloudFunctionsNamespace,
            '--cloudfunctions_package', cls.cloudFunctionsPackage,
            '--cloudfunctions_function', cls.cloudFunctionsFunction,
            '--cloudfunctions_username', cls.cloudFunctionsUsername,
            '--cloudfunctions_password', cls.cloudFunctionsPassword
        ]
        # create output folder
        BaseTestCaseCapture.createFolder(TestMain.testOutputPath)

    def callfunc(self, *args, **kwargs):
        args = list(args)[0] + ['--version', '2.2']
        functions_test.main(args, **kwargs)

    def test_args_basic(self):
        ''' Tests some basic sets of args '''
        self.t_missingRequiredArgs([[]])
        self.t_missingRequiredArgs([['/some/random/path']])
        self.t_unrecognizedArgs([['/some/random/path', '-s', 'randomNonPositionalArg']])

    def test_args_advanced(self):
        ''' Tests cloud function sets of args '''
        for missingTestArgIndex, missingTestArg in enumerate(self.functionsTestArgs[::2]):
            providedTestArgs = list(self.functionsTestArgs)
            del providedTestArgs[2 * missingTestArgIndex + 1]
            del providedTestArgs[2 * missingTestArgIndex]

            providedTestArgs = ['/some/random/path', '/some/random/path'] + providedTestArgs
            if missingTestArg in ['--cloudfunctions_package', '--cloudfunctions_function']:
                self.t_exitCodeAndLogMessage(
                    1, # exit code
                    'WARNING  \'' + missingTestArg[2:] + '\' parameter not defined', # warning message substring
                    [providedTestArgs] # params (*args, **kwargs)
                )
            elif missingTestArg in ['--cloudfunctions_username', '--cloudfunctions_password']:
                self.t_exitCodeAndLogMessage(
                    1, # exit code
                    'CRITICAL part of parameters combination is set, but some params are missing', # critical message substring
                    [providedTestArgs] # params (*args, **kwargs)
                )
            else:
                self.t_exitCodeAndLogMessage(
                    1, # exit code
                    'ERROR    required \'' + missingTestArg[2:] + '\' parameter not defined', # error message substring
                    [providedTestArgs] # params (*args, **kwargs)
                )

    def test_args_invalidReplaceFormat(self):
        ''' Tests if treplace format is invalid '''
        testArgs = [self.testSingleAllInFileJsonPath, self.outputCommonPath] + self.functionsTestArgs
        for invalidReplaceFormat in ['xxx', 'xxx:', ':xxx', 'xxx:yyy:zzz', 'xxx:yyy,', ',xxx:yyy', 'xxx:yyy,ccc']:
            self.t_exitCodeAndLogMessage(
                1, # exit code
                'CRITICAL Invalid format of \'replace\' parameter', # critical message substring
                [testArgs +  ['--replace', invalidReplaceFormat]] # params (*args, **kwargs)
            )

    def test_nonExistentFileInput(self):
        ''' Tests if the input file does not exist '''
        testArgs = ['/some/random/path', '/some/random/path'] + self.functionsTestArgs
        self.t_exitCodeAndLogMessage(
            1, # exit code
            'CRITICAL Cannot open test input file /some/random/path', # critical message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_nonExistentFileOutput(self):
        ''' Tests if the output file does not exist '''
        testArgs = [self.noJsonPath, '/some/random/path'] + self.functionsTestArgs
        self.t_exitCodeAndLogMessage(
            1, # exit code
            'CRITICAL Cannot open test output file /some/random/path', # critical message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_invalidJsonInput(self):
        ''' Tests if the input file contains invalid json '''
        testArgs = [self.noJsonPath, self.outputCommonPath] + self.functionsTestArgs
        self.t_exitCodeAndLogMessage(
            1, # exit code
            'CRITICAL Cannot decode json from test input file', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_nonArrayJsonInput(self):
        ''' Tests if the input file contains non array json '''
        testArgs = [self.emptyDictJsonPath, self.outputCommonPath] + self.functionsTestArgs
        self.t_exitCodeAndLogMessage(
            1, # exit code
            'CRITICAL Input test json is not array!', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSingleInvalid(self):
        ''' Tests if the input file contains test that is not dictionary '''
        testArgs = [self.testSingleInvalidJsonPath, self.outputCommonPath] + self.functionsTestArgs
        self.t_noExceptionAndLogMessage(
            'ERROR    Input test array element 0 is not dictionary. Each test has to be dictionary, please see doc!', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSingleAllInFileBadAuthentification(self):
        ''' Tests if bad authentification was provided '''
        testArgs = [self.testSingleAllInFileJsonPath, self.outputCommonPath] + self.functionsTestArgs
        testArgs[testArgs.index('--cloudfunctions_password') + 1] = 'invalidPassword' # change password to something different
        self.t_exitCodeAndLogMessage(
            1, # exit code
            'The supplied authentication is invalid', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSingleAllInFileBadUrl(self):
        ''' Tests if bad url was provided '''
        testArgs = [self.testSingleAllInFileJsonPath, self.outputCommonPath] + self.functionsTestArgs
        testArgs[testArgs.index('--cloudfunctions_url') + 1] = 'https://us-south.functions.cloud.ibm.com/invalidUrl' # change password to something different
        self.t_noExceptionAndLogMessage(
            '404 Not Found', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    def test_testSingleAllInFile(self):
        ''' Tests if the single test where input and expected output is specified
         in file (all other params are given from command line) '''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.splitext(os.path.basename(self.testSingleAllInFileJsonPath))[0] + '.out.json'))
        testArgs = [self.testSingleAllInFileJsonPath, outputFilePath] + self.functionsTestArgs
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
                    }
                }
            ]

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    def test_testSingleAllInFileReplace(self):
        ''' Tests if the single test where input and expected output is specified
         in file (all other params are given from command line), using replace
         functionality (using --replace_)'''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.splitext(os.path.basename(self.testSingleAllInFileReplaceJsonPath))[0] + '.out.json'))
        testArgs = [self.testSingleAllInFileReplaceJsonPath, outputFilePath] + self.functionsTestArgs + ['--replace', 'OUTPUT_EXPECTED_MESSAGE:test message']
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
                    }
                }
            ]

    def test_testSingleAllInFileReplacePackage(self):
        ''' Tests if the single test where input and expected output is specified
         in file (all other params are given from command line), using replace
         functionality (using standard config parameter)'''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.splitext(os.path.basename(self.testSingleAllInFileReplacePackageJsonPath))[0] + '.out.json'))
        testArgs = [self.testSingleAllInFileReplacePackageJsonPath, outputFilePath] + self.functionsTestArgs
        self.t_noException([testArgs])
        with open(outputFilePath, 'r') as outputFile:
            outputJson = json.load(outputFile)
            assert outputJson == [
                {
                    "input": {
                        "message": "utils"
                    },
                    "outputReturned": {
                        "message": "utils"
                    },
                    "outputExpected": {
                        "message": "utils"
                    }
                }
            ]

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    def test_testSinglePayloadsOut(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file (all other params are given from command line) '''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.splitext(os.path.basename(self.testSinglePayloadsOutJsonPath))[0] + '.out.json'))
        testArgs = [self.testSinglePayloadsOutJsonPath, outputFilePath] + self.functionsTestArgs
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
                    }
                }
            ]

    def test_testSinglePayloadsOutNonExistingInput(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file but input path is wrong (all other params are given from command line) '''
        testArgs = [self.testSinglePayloadsOutNonExistingInputJsonPath, self.outputCommonPath] + self.functionsTestArgs
        self.t_noExceptionAndLogMessage(
            'ERROR    Cannot open input payload from file: /some/random/path', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSinglePayloadsOutNoJsonInput(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file but input is invalid json
         (all other params are given from command line) '''
        testArgs = [self.testSinglePayloadsOutNoJsonInputJsonPath, self.outputCommonPath] + self.functionsTestArgs
        self.t_noExceptionAndLogMessage(
            'ERROR    Cannot decode json from input payload from file', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSinglePayloadsOutNonExistingOutput(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file but expected output path
         is wrong (all other params are given from command line) '''
        testArgs = [self.testSinglePayloadsOutNonExistingOutputJsonPath, self.outputCommonPath] + self.functionsTestArgs
        self.t_noExceptionAndLogMessage(
            'ERROR    Cannot open expected output payload from file: /some/random/path', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    def test_testSinglePayloadsOutNoJsonOutput(self):
        ''' Tests if the single test where input and expected output is specified
         in another file - by relative path to that file but expected output
         is invalid json (all other params are given from command line) '''
        testArgs = [self.testSinglePayloadsOutNoJsonOutputJsonPath, self.outputCommonPath] + self.functionsTestArgs
        self.t_noExceptionAndLogMessage(
            'ERROR    Cannot decode json from expected output payload from file', # error message substring
            [testArgs] # params (*args, **kwargs)
        )

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    def test_testSingleAllInFileOverridePackage(self):
        ''' Tests if bad package was provided in test it self, the main reason is test that override works '''
        testArgs = [self.testSingleAllInFileOverridePackageJsonPath, self.outputCommonPath] + self.functionsTestArgs
        self.t_noExceptionAndLogMessage(
            'actions/BAD_PACKAGE/echo', # log message substring
            [testArgs] # params (*args, **kwargs)
        )

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    def test_testSingleAllInFileOverrideFunction(self):
        ''' Tests if bad function was provided in test it self, the main reason is test that override works '''
        testArgs = [self.testSingleAllInFileOverrideFunctionJsonPath, self.outputCommonPath] + self.functionsTestArgs
        self.t_noExceptionAndLogMessage(
            'actions/utils/BAD_FUNCTION', # log message substring
            [testArgs] # params (*args, **kwargs)
        )

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    @pytest.mark.parametrize('useApikey', [True, False])
    def test_testMulti(self, useApikey):
        ''' Tests if there are multi tests in input file '''
        outputFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.splitext(os.path.basename(self.testMultiJsonPath))[0] + '.out.json'))
        testArgs = [self.testMultiJsonPath, outputFilePath] + self.functionsTestArgs

        if useApikey:
            testArgs = testArgs[:len(testArgs)-4] # remove password, username and their values
            testArgs.extend(['--cloudfunctions_apikey', self.cloudFunctionsUsername + ':' + self.cloudFunctionsPassword])

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
                    }
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
                    }
                }
            ]
