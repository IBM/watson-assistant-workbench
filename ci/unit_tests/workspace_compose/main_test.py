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

import os, pytest, argparse, json

import workspace_compose
from cfgCommons import Cfg
from wawCommons import openFile
from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    outputPath = os.path.join(dataBasePath, 'outputs')

    def setup_class(cls):
        BaseTestCaseCapture.createFolder(cls.outputPath)

        cls.composeParamsBase = ['--common_outputs_directory', cls.dataBasePath,
                                '-v']

    def callfunc(self, *args, **kwargs):
        workspace_compose.main(*args, **kwargs)

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_allFromFileAndAllFromConfiguration(self):
        """Tests if all intents, entities and dialog from files and name,
         description and language from configuration are contained in
         output workspace."""

        workspaceFilename = 'skill_with_all_info.json'
        workspaceName = 'Configuration-defined workspace name'
        workspaceDescription = "Configuration-defined skill description"

        # deploy test workspace with descriptiton and name defined in json
        composeParams = list(self.composeParamsBase)
        composeParams.extend(['--common_outputs_directory', self.outputPath,
                              '--common_outputs_workspace', workspaceFilename,
                              '--conversation_workspace_name', workspaceName,
                              '--conversation_language', 'en',
                              '--conversation_description', workspaceDescription,
                              '--common_outputs_intents', os.path.join(self.dataBasePath, 'intents.json'),
                              '--common_outputs_entities', os.path.join(self.dataBasePath, 'entities.json'),
                              '--common_outputs_dialogs', os.path.join(self.dataBasePath, 'dialog.json')])

        self.t_noException([composeParams])

        # script output
        with openFile(os.path.join(self.outputPath, workspaceFilename), 'r', encoding='utf8') as outputFile:
            outputWorkspaceJSON = json.load(outputFile)

            # expected output
            with openFile(os.path.join(self.dataBasePath, workspaceFilename), 'r', encoding='utf8') as expectedFile:
                expectedWorkspaceJSON = json.load(expectedFile)

                assert json.dumps(outputWorkspaceJSON, sort_keys=True) == json.dumps(expectedWorkspaceJSON, sort_keys=True)


    def test_allFromFileAndNoneFromConfiguration(self):
        """Tests if all intents, entities and dialog from files and
         default values for name, description and language are contained in
         output workspace."""

        workspaceFilename = 'skill_without_name_and_description.json'

        # deploy test workspace with descriptiton and name defined in json
        composeParams = list(self.composeParamsBase)
        composeParams.extend(['--common_outputs_directory', self.outputPath,
                              '--common_outputs_workspace', workspaceFilename,
                              '--common_outputs_intents', os.path.join(self.dataBasePath, 'intents.json'),
                              '--common_outputs_entities', os.path.join(self.dataBasePath, 'entities.json'),
                              '--common_outputs_dialogs', os.path.join(self.dataBasePath, 'dialog.json')])

        self.t_noException([composeParams])

        # script output
        with openFile(os.path.join(self.outputPath, workspaceFilename), 'r', encoding='utf8') as outputFile:
            outputWorkspaceJSON = json.load(outputFile)

            # expected output
            with openFile(os.path.join(self.dataBasePath, workspaceFilename), 'r', encoding='utf8') as expectedFile:
                expectedWorkspaceJSON = json.load(expectedFile)

                assert json.dumps(outputWorkspaceJSON, sort_keys=True) == json.dumps(expectedWorkspaceJSON, sort_keys=True)


    def test_args_basic(self):
        ''' Tests some basic sets of args '''

        self.t_unrecognizedArgs([['--nonExistentArg', 'randomNonPositionalArg']])
        # at least one argument (configfile) has to be defined
        self.t_exitCode(1, [[]])
        # check missing required args
        requiredArgsList = ['--common_outputs_directory', self.dataBasePath]
        # ommit each of them
        for argIndex in range(len(requiredArgsList)):
            if not requiredArgsList[argIndex].startswith('--'):
                continue
            paramName = requiredArgsList[argIndex][2:]

            argsListWithoutOne = []
            for i in range(len(requiredArgsList)):
                if i != argIndex and i != (argIndex + 1):
                    argsListWithoutOne.append(requiredArgsList[i])

            message = 'required \'' + paramName + '\' parameter not defined'
            self.t_exitCodeAndLogMessage(1, message, [argsListWithoutOne])
