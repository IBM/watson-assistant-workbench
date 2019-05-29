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

import functions_test
import functions_test_evaluate

from ..test_utils import BaseTestCaseCapture


class TestTestAndEvaluateFunction(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testAndEvaluateFunction_data')
    testOutputPath = os.path.join(dataBasePath, 'outputs')

    testSingleAllInFileReplacePackageJsonPath = os.path.abspath(os.path.join(dataBasePath, 'test_single_all_in_file_replace_package.json'))

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
        BaseTestCaseCapture.createFolder(TestTestAndEvaluateFunction.testOutputPath)

    def test_testSingleAllInFileReplacePackage(self):
        ''' Tests if the single test where input and expected output is specified
         in file (all other params are given from command line), using replace
         functionality (using standard config parameter)'''
        testSingleAllInFileReplacePackageOutJsonPath = os.path.abspath(os.path.join(self.testOutputPath, os.path.splitext(os.path.basename(self.testSingleAllInFileReplacePackageJsonPath))[0] + '.out.json'))
        testSingleAllInFileReplacePackageEvalJsonPath = os.path.abspath(os.path.join(self.testOutputPath, os.path.splitext(os.path.basename(self.testSingleAllInFileReplacePackageJsonPath))[0] + '.eval.json'))
        testSingleAllInFileReplacePackageEvaJUnitXmlFilePath = os.path.abspath(os.path.join(self.testOutputPath, os.path.basename(self.testSingleAllInFileReplacePackageJsonPath).split('.')[0] + '.eval.junit.xml'))

        testArgs = [self.testSingleAllInFileReplacePackageJsonPath, testSingleAllInFileReplacePackageOutJsonPath] + self.functionsTestArgs
        self.t_fun_noException(functions_test.main, [testArgs + ['--version', '2.2', '-t']])

        testArgs = [testSingleAllInFileReplacePackageOutJsonPath, testSingleAllInFileReplacePackageEvalJsonPath]
        self.t_fun_noException(functions_test_evaluate.main, [testArgs + ['-j', testSingleAllInFileReplacePackageEvaJUnitXmlFilePath]])

        with open(testSingleAllInFileReplacePackageEvalJsonPath, 'r') as outputFile:
            outputJson = json.load(outputFile)
            assert isinstance(outputJson[0]['start'], int)
            assert isinstance(outputJson[0]['end'], int)
            assert isinstance(outputJson[0]['time'], int)
            del outputJson[0]['start']
            del outputJson[0]['end']
            del outputJson[0]['time']
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
                    },
                    "result": 0
                }
            ]

        with open(testSingleAllInFileReplacePackageEvaJUnitXmlFilePath, 'r') as outputFile:
            outputString = outputFile.read()
            outputString = re.sub(r'time="[0-9\.]+"', 'time="TIME"', outputString)
            outputString = re.sub(r'timestamp="[0-9\.:\- ]+"', 'timestamp="TIMESTAMP"', outputString)
            assert outputString == \
                '<?xml version="1.0" encoding="utf-8"?>\n' +\
                '<testsuites errors="0" failures="0" tests="1" time="TIME">\n' +\
                '\t<testsuite errors="0" failures="0" name="test_single_all_in_file_replace_package.out" ' +\
                    'skipped="0" tests="1" time="TIME" timestamp="TIMESTAMP">\n' +\
                '\t\t<testcase time="TIME"/>\n' +\
                '\t</testsuite>\n' +\
                '</testsuites>\n'
