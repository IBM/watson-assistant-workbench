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

import os, pytest, re
import lxml.etree as LET

import dialog_json2xml
import dialog_xls2xml
import dialog_xml2json
import evaluate_tests
import entities_csv2json
import entities_json2csv
import intents_csv2json
import intents_json2csv
import workspace_compose
import workspace_decompose
import workspace_deploy
import workspace_test
from ..test_utils import BaseTestCaseCapture

class TestGenerateAndTestWorkspace(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'generateAndTestWorkspace_data' + os.sep)
    testOutputPath = os.path.join(dataBasePath, 'outputs')

    def setup_class(cls):
        ''' Setup any state specific to the execution of the given class (which usually contains tests). '''
        BaseTestCaseCapture.createFolder(TestGenerateAndTestWorkspace.testOutputPath)

    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword, envVarNameWorkspaceId', [('WA_USERNAME', 'WA_PASSWORD', 'WA_WORKSPACE_ID_TEST')])
    def test_basic(self, envVarNameUsername, envVarNamePassword, envVarNameWorkspaceId):
        ''' Tests whole WAW pipeline. Test expects that envVarNameUsername, envVarNamePassword and envVarNameWorkspaceId are set in environment variables. '''

        # check environment variables
        BaseTestCaseCapture.checkEnvironmentVariables([envVarNameUsername, envVarNamePassword, envVarNameWorkspaceId])

        # define and create all filenames, paths and folders
        jsonDialogFilename = 'dialog.json'
        jsonEntitiesFilename = 'entities.json'
        jsonIntentsFilename = 'intents.json'
        jsonWorkspaceFilename = 'workspace.json'
        jsonWorkspacePath = os.path.abspath(os.path.join(self.testOutputPath, jsonWorkspaceFilename))
        jsonDecomposedDialogPath = os.path.abspath(os.path.join(self.testOutputPath, 'dialogDecomposed.json'))
        jsonDecomposedEntitiesPath = os.path.abspath(os.path.join(self.testOutputPath, 'entitiesDecomposed.json'))
        jsonDecomposedIntentsPath = os.path.abspath(os.path.join(self.testOutputPath, 'intentsDecomposed.json'))
        dialogsFolderPath = os.path.abspath(os.path.join(self.dataBasePath, 'dialogs'))
        entitiesFolderPath = os.path.abspath(os.path.join(self.dataBasePath, 'entities'))
        intentsFolderPath = os.path.abspath(os.path.join(self.dataBasePath, 'intents'))
        dialogsDecomposedFolderPath = os.path.abspath(os.path.join(self.testOutputPath, 'd_dialogs'))
        entitiesDecomposedFolderPath = os.path.abspath(os.path.join(self.testOutputPath, 'd_entities'))
        intentsDecomposedFolderPath = os.path.abspath(os.path.join(self.testOutputPath, 'd_intents'))
        dialogMainPath = os.path.abspath(os.path.join(dialogsFolderPath, 'main.xml'))
        configBuildPath = os.path.abspath(os.path.join(self.dataBasePath, 'build.cfg'))
        configTestPath = os.path.abspath(os.path.join(self.dataBasePath, 'test.cfg'))
        configTmpPath = os.path.abspath(os.path.join(self.testOutputPath, 'tmp.cfg'))
        generatedDialogsFolderPath = os.path.abspath(os.path.join(self.testOutputPath, 'g_dialogs'))
        generatedIntentsFolderPath = os.path.abspath(os.path.join(self.testOutputPath, 'g_intents'))
        generatedEntitiesFolderPath = os.path.abspath(os.path.join(self.testOutputPath, 'g_entities'))
        xlsFolderPath = os.path.abspath(os.path.join(self.dataBasePath, 'xls'))
        xlsEnMasterPath = os.path.abspath(os.path.join(xlsFolderPath, 'E_EN_master.xlsx'))
        xlsEnTestsPath = os.path.abspath(os.path.join(xlsFolderPath, 'E_EN_tests.xlsx'))
        xlsEnT2CAuthoringPath = os.path.abspath(os.path.join(xlsFolderPath, 'E_EN_T2C_authoring.xlsx'))
        xlsCzT2CAuthoringPath = os.path.abspath(os.path.join(xlsFolderPath, 'E_CZ_T2C_authoring.xlsx'))
        xlsCondXTestPath = os.path.abspath(os.path.join(xlsFolderPath, 'cond_x_test.xlsx'))
        testDummyRefPath = os.path.abspath(os.path.join(self.dataBasePath, 'test_dummy.test'))
        testDummyHypPath = os.path.abspath(os.path.join(self.testOutputPath, 'test_dummy.out'))
        testDummyJUnitPath = os.path.abspath(os.path.join(self.testOutputPath, 'test_dummy.junit.xml'))
#        testMoreOutputsRefPath = os.path.abspath(os.path.join(self.dataBasePath, 'test_more_outputs.test'))
#        testMoreOutputsHypPath = os.path.abspath(os.path.join(self.testOutputPath, 'test_more_outputs.out'))
#        testMoreOutputsJUnitPath = os.path.abspath(os.path.join(self.testOutputPath, 'test_more_outputs.junit.xml'))
#        testNillRefPath = os.path.abspath(os.path.join(self.dataBasePath, 'test_nill.test'))
#        testNillHypPath = os.path.abspath(os.path.join(self.testOutputPath, 'test_nill.out'))
#        testNillJUnitPath = os.path.abspath(os.path.join(self.testOutputPath, 'test_nill.junit.xml'))
        BaseTestCaseCapture.createFolders([generatedDialogsFolderPath, generatedIntentsFolderPath, generatedEntitiesFolderPath])
        BaseTestCaseCapture.createFolders([dialogsDecomposedFolderPath, entitiesDecomposedFolderPath, intentsDecomposedFolderPath])

        # convert xls files to xml dialogs, intents and entities
        self.t_fun_noException(dialog_xls2xml.main, [['-x', xlsEnMasterPath, '-gd', generatedDialogsFolderPath, '-gi', generatedIntentsFolderPath, '-ge', generatedEntitiesFolderPath, '-v']])
        self.t_fun_noException(dialog_xls2xml.main, [['-x', xlsEnTestsPath, '-gd', generatedDialogsFolderPath, '-gi', generatedIntentsFolderPath, '-ge', generatedEntitiesFolderPath, '-v']])
        self.t_fun_noException(dialog_xls2xml.main, [['-x', xlsEnT2CAuthoringPath, '-gd', generatedDialogsFolderPath, '-gi', generatedIntentsFolderPath, '-ge', generatedEntitiesFolderPath, '-v']])
        self.t_fun_noException(dialog_xls2xml.main, [['-x', xlsCzT2CAuthoringPath, '-gd', generatedDialogsFolderPath, '-gi', generatedIntentsFolderPath, '-ge', generatedEntitiesFolderPath, '-v']])
        self.t_fun_noException(dialog_xls2xml.main, [['-x', xlsCondXTestPath, '-gd', generatedDialogsFolderPath, '-gi', generatedIntentsFolderPath, '-ge', generatedEntitiesFolderPath, '-v']])

        # testing entities in T2C (@entity:(<x>) blocks)
        xmlCondXTestPath = os.path.abspath(os.path.join(generatedDialogsFolderPath, 'cond_x_test.xml'))
        with open(xmlCondXTestPath, 'r') as file:
            fileContent = file.read()
            # it is necessary to have 'Z.*vada' because original word to be matched, 'Z<A-ACUTE>vada', is represented like 'Z\xc3\xa1vada', same thing for others patterns
            assert re.compile('#CO_JE.*@PREDMET:\(Z.*vada\)').search(fileContent)
            assert re.compile('#CO_JE.*@PREDMET:\(V.*stra.*n.* stav\)').search(fileContent)
            assert re.compile('#CO_JE.*@PREDMET:\(Vyrovn.*vac.* trh\)').search(fileContent)
            assert re.compile('#CO_JE.*@PREDMET:\(Buttons do not belong here\)').search(fileContent)

        # convert dialog from xml to json
        self.t_fun_noException(dialog_xml2json.main, [['-dm', dialogMainPath, '-of', self.testOutputPath, '-od', jsonDialogFilename, '-s', self.dialogSchemaPath, '-c', configBuildPath, '-v']])

        # convert entities from csv to json
        self.t_fun_noException(entities_csv2json.main, [['-ie', entitiesFolderPath, '-od', self.testOutputPath, '-oe', jsonEntitiesFilename, '-v']])

        # convert intents from csv to json
        self.t_fun_noException(intents_csv2json.main, [['-ii', intentsFolderPath, '-od', self.testOutputPath, '-oi', jsonIntentsFilename, '-v']])

        # compose dialog, intent and entity json files to one workspace
        self.t_fun_noException(workspace_compose.main, [['-of', self.testOutputPath, '-ow', jsonWorkspaceFilename, '-od', jsonDialogFilename, '-oe', jsonEntitiesFilename, '-oi', jsonIntentsFilename, '-v']])

        # decompose workspace to dialog, intent and entity json files
        self.t_fun_noException(workspace_decompose.main, [[jsonWorkspacePath, '-d', jsonDecomposedDialogPath, '-e', jsonDecomposedEntitiesPath, '-i', jsonDecomposedIntentsPath, '-v']])

        # convert dialog from json to xml
        self.t_fun_noException(dialog_json2xml.main, [[jsonDecomposedDialogPath, '-d', dialogsDecomposedFolderPath, '-v']])

        # convert entities from json to csv
        self.t_fun_noException(entities_json2csv.main, [[jsonDecomposedEntitiesPath, entitiesDecomposedFolderPath, '-v']])

        # convert intents from json to csv
        self.t_fun_noException(intents_json2csv.main, [[jsonDecomposedIntentsPath, intentsDecomposedFolderPath, '-v']])

        # deploy test workspace
        self.t_fun_noException(workspace_deploy.main, [['-of', self.testOutputPath, '-ow', jsonWorkspaceFilename, '-c', configTestPath, '-cn', os.environ[envVarNameUsername], '-cp', os.environ[envVarNamePassword], '-cid', os.environ[envVarNameWorkspaceId], '-v']])

        # test against test workspace
        with open(configTestPath, 'r') as configTest, open(configTmpPath, 'w') as configTmp:
            configTmp.write(configTest.read())
            configTmp.write('username = ' + os.environ[envVarNameUsername] + '\n')
            configTmp.write('password = ' + os.environ[envVarNamePassword] + '\n')
            configTmp.write('workspace_id = ' + os.environ[envVarNameWorkspaceId] + '\n')
        self.t_fun_noException(workspace_test.main, [[testDummyRefPath, testDummyHypPath, '-c', configTmpPath, '-v']])
#        self.t_fun_noException(workspace_test.main, [[testMoreOutputsRefPath, testMoreOutputsHypPath, '-c', configTmpPath, '-v']])
#        self.t_fun_noException(workspace_test.main, [[testNillRefPath, testNillHypPath, '-c', configTmpPath, '-v']])

        # evaluate tests
        self.t_fun_noException(evaluate_tests.main, [[testDummyRefPath, testDummyHypPath, '-o', testDummyJUnitPath, '-v']])
#        self.t_fun_noException(evaluate_tests.main, [[testMoreOutputsRefPath, testMoreOutputsHypPath, '-o', testMoreOutputsJUnitPath, '-v']])
#        self.t_fun_noException(evaluate_tests.main, [[testNillRefPath, testNillHypPath, '-o', testNillJUnitPath, '-v']])
        testDummyJUnitXmlTree = LET.parse(testDummyJUnitPath)
#        testMoreOutputsJUnitXmlTree = LET.parse(testMoreOutputsJUnitPath)
#        testNillJUnitXmlTree = LET.parse(testNillJUnitPath)
        assert testDummyJUnitXmlTree.getroot().tag == 'testsuites'
#        assert testMoreOutputsJUnitXmlTree.getroot().tag == 'testsuites'
#        assert testNillJUnitXmlTree.getroot().tag == 'testsuites'
        assert testDummyJUnitXmlTree.getroot().get('failures') == '0'
#        assert testMoreOutputsJUnitXmlTree.getroot().get('failures') == '0'
#        assert testNillJUnitXmlTree.getroot().get('failures') == '0'

        # TODO: should be fixed in evaluate_tests.main (and test itself), right now it does not report errors to junit xml file, but just to the standard output
        # step 1: uncomment lines below and fix test to pass
        # step 2: fix evaluate_tests.main to report errors to junit xml file, use output properly and remove lines below
        #if 'ERROR' in self.captured.err:
            #pytest.fail('ERROR found in err log of evaluate_tests.main, log:\n' + self.captured.err)
        #if 'ERROR' in self.captured.out:
            #pytest.fail('ERROR found in out log of evaluate_tests.main, log:\n' + self.captured.out)
