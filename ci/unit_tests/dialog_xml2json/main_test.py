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
import lxml
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
                            '--common_outputs_directory', outputJsonDirPath,
                            '--common_schema', self.dialogSchemaPath]])


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

    def test_mainValidNodeTypes(self):
        """Tests if the script successfully completes with valid input file with node types."""
        inputXmlPath = os.path.abspath(os.path.join(self.dataBasePath, 'inputNodeTypesValid.xml'))
        expectedJsonPath = os.path.abspath(os.path.join(self.dataBasePath, 'expectedNodeTypesValid.json'))

        outputJsonDirPath = os.path.join(self.testOutputPath, 'outputNodeTypesValidResult')
        outputJsonPath = os.path.join(outputJsonDirPath, 'dialog.json')

        BaseTestCaseCapture.createFolder(outputJsonDirPath)

        self.t_noException([['--common_dialog_main', inputXmlPath,
                            '--common_outputs_dialogs', 'dialog.json',
                            '--common_outputs_directory', outputJsonDirPath,
                            '--common_schema', self.dialogSchemaPath]])

        with open(expectedJsonPath, 'r') as expectedJsonFile, open(outputJsonPath, 'r') as outputJsonFile:
            assert json.load(expectedJsonFile) == json.load(outputJsonFile)


    def test_mainMissingImport(self):
        """Tests if the script fails with file with missing imported dialog file."""
        inputXmlPath = os.path.abspath(os.path.join(self.dataBasePath, 'inputMissingImport.xml'))
        inputXmlDir = os.path.dirname(os.path.abspath(inputXmlPath))
        importedXmlPath = os.path.join(inputXmlDir, "nonexistentImport.xml")
        self.t_exitCodeAndLogMessage(1, "Imported dialog file " + importedXmlPath + " not found.",
                                    [['--common_dialog_main', inputXmlPath]])


    def test_missingRoot(self):
        """Tests if the script fails with file with missing root dialog file."""

        self.t_exitCodeAndLogMessage(1, "Root dialog file nonexistentInputFile.xml not found.",
                                    [['--common_dialog_main', 'nonexistentInputFile.xml']])


    def test_validation(self):
        """Tests if the script runs successfully with valid dialogs and fails with invalid dialog files."""

        inputOutputMsg = [
            ("autogenerate_typeValid.xml", "autogenerate_typeInvalid.xml",
            "Element 'autogenerate': The attribute 'type' is required but missing."),
            ("goto_targetValid.xml", "goto_targetInvalid.xml",
            "Element 'goto': Missing child element(s). Expected is one of ( behavior, target )."),
            ("node_attributeValid.xml", "node_attributeInvalid.xml",
            "Element 'node', attribute 'nonexistentAttribute': The attribute 'nonexistentAttribute' is not allowed."),
            ("node_singleElementValid.xml", "node_singleElementInvalid.xml",
            "Element 'condition': This element is not expected."),
            ("nodes_subElementsValid.xml", "nodes_subElementsInvalid.xml",
            "Element 'outputs': This element is not expected. Expected is one of ( import, autogenerate, node )."),
        ]

        validInputsFolder = os.path.join(self.dataBasePath, "validInputsAccordingToSchema")
        invalidInputsFolder = os.path.join(self.dataBasePath, "invalidInputsAccordingToSchema")

        for triplet in inputOutputMsg:
            validXmlPath = os.path.abspath(os.path.join(validInputsFolder, triplet[0]))
            invalidXmlPath = os.path.abspath(os.path.join(invalidInputsFolder, triplet[1]))

            self.t_noException([['--common_dialog_main', validXmlPath,
                                    '--common_schema', self.dialogSchemaPath]])

            msg = triplet[2]

            self.t_exitCodeAndLogMessage(1, msg,
                                    [['--common_dialog_main', invalidXmlPath,
                                    '--common_schema', self.dialogSchemaPath]])
    def test_mainInvalidNodeTypes(self):
        """Tests if the script fails with input file with invalid node type."""
        inputXmlPath = os.path.abspath(os.path.join(self.dataBasePath, 'inputNodeTypesInvalid.xml'))

        self.t_exitCodeAndLogMessage(1, "The value 'random_type' is not an element of the set",
                            [['--common_dialog_main', inputXmlPath, '--common_schema', self.dialogSchemaPath]])
