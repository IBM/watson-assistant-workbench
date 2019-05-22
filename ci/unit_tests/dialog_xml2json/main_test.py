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

import dialog_xml2json

from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    testOutputPath = os.path.join(dataBasePath, 'outputs')


    def setup_class(cls):
        ''' Setup any state specific to the execution of the given class (which usually contains tests). '''
        # create output folder
        BaseTestCaseCapture.createFolder(TestMain.testOutputPath)

    def callfunc(self, *args, **kwargs):
        dialog_xml2json.main(*args, **kwargs)

    def test_mainValidActions(self):
        """Tests if the script successfully completes with valid input file with actions."""
        inputXmlPath = os.path.abspath(os.path.join(self.dataBasePath, 'inputActionsValid.xml'))
        expectedJsonPath = os.path.abspath(os.path.join(self.dataBasePath, 'expectedActionsValid.json'))

        outputJsonDirPath = os.path.join(self.testOutputPath, 'outputActionsValidResult')
        outputJsonPath = os.path.join(outputJsonDirPath, 'dialog.json')

        BaseTestCaseCapture.createFolder(outputJsonDirPath)

        self.t_noException([['--common_dialog_main', inputXmlPath,
                            '--common_outputs_dialogs', 'dialog.json',
                            '--common_outputs_directory', outputJsonDirPath]])


        with open(expectedJsonPath, 'r') as expectedJsonFile, open(outputJsonPath, 'r') as outputJsonFile:
            assert json.load(expectedJsonFile) == json.load(outputJsonFile)

    def test_mainValidBool(self):
        """Tests if the script successfully completes with valid input file with bools."""
        inputXmlPath = os.path.abspath(os.path.join(self.dataBasePath, 'inputBoolValid.xml'))
        expectedJsonPath = os.path.abspath(os.path.join(self.dataBasePath, 'expectedBoolValid.json'))

        outputJsonDirPath = os.path.join(self.testOutputPath, 'outputBoolValidResult')
        outputJsonPath = os.path.join(outputJsonDirPath, 'dialog.json')

        BaseTestCaseCapture.createFolder(outputJsonDirPath)

        self.t_noException([['--common_dialog_main', inputXmlPath,
                            '--common_outputs_dialogs', 'dialog.json',
                            '--common_outputs_directory', outputJsonDirPath]])

        with open(expectedJsonPath, 'r') as expectedJsonFile, open(outputJsonPath, 'r') as outputJsonFile:
            assert json.load(expectedJsonFile) == json.load(outputJsonFile)
