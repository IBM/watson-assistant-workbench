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

import os, pytest, requests, argparse, uuid

import workspace_deploy, workspace_delete
from cfgCommons import Cfg
from wawCommons import getWorkspaces
from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    outputPath = os.path.join(dataBasePath, 'outputs')
    workspacesUrl = 'https://gateway.watsonplatform.net/conversation/api/v1/workspaces'
    version = '2017-02-03'

    def setup_class(cls):
        BaseTestCaseCapture.createFolder(cls.outputPath)
        BaseTestCaseCapture.checkEnvironmentVariables(['WA_USERNAME', 'WA_PASSWORD'])
        cls.username = os.environ['WA_USERNAME']
        cls.password = os.environ['WA_PASSWORD']

        cls.deployParamsBase = ['--common_outputs_directory', cls.dataBasePath,
                                '--conversation_username', cls.username,
                                '--conversation_password', cls.password,
                                '--conversation_url', cls.workspacesUrl,
                                '--conversation_version', cls.version,
                                '-v']

        cls.deleteParamsBase = ['--conversation_username', cls.username,
                                '--conversation_password', cls.password,
                                '--conversation_url', cls.workspacesUrl,
                                '--conversation_version', cls.version,
                                '--conversation_workspace_match_by_name', 'true',
                                '--conversation_workspace_name_pattern', '.*',
                                '-v']

    def callfunc(self, *args, **kwargs):
        workspace_deploy.main(*args, **kwargs)

    def setup_method(self):
        workspace_delete.main(self.deleteParamsBase)

    def teardown_method(self):
        workspace_delete.main(self.deleteParamsBase)


    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_nameAndDescriptionSetup(self, envVarNameUsername, envVarNamePassword):
        """Tests if name and description from json is uploaded, it is not overriden
         by empty settings and can be overriden by configuration parameters."""

        jsonWorkspaceFilename = 'skill_with_name_and_description.json'
        jsonWorkspaceUpdateFilename = 'skill_without_name_and_description.json'
        workspaceName = 'Configuration-defined workspace name'

        # deploy test workspace with descriptiton and name defined in json
        deployParams = list(self.deployParamsBase)
        deployParams.extend(['--common_outputs_workspace', jsonWorkspaceFilename])

        self.t_noExceptionAndLogMessage("Workspace successfully uploaded.", [deployParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        assert len(workspaces) == 1

        # check if json setting was uploaded
        assert workspaces[0]['name'] == "Customer Care Sample Skill"
        assert workspaces[0]['description'] == "A sample simple Customer Service skill"

        workspaceId = workspaces[0]['workspace_id']

        # update test workspace without descriptiton and name
        deployParams = list(self.deployParamsBase)
        deployParams.extend(['--common_outputs_workspace', jsonWorkspaceUpdateFilename,
                             '--conversation_workspace_id', workspaceId])

        self.t_noExceptionAndLogMessage("Workspace successfully uploaded.", [deployParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        assert len(workspaces) == 1

        # description and name should remain the same
        assert workspaces[0]['name'] == "Customer Care Sample Skill"
        assert workspaces[0]['description'] == "A sample simple Customer Service skill"

        # update test workspace with the one with name while having name as parameter
        deployParams = list(self.deployParamsBase)
        deployParams.extend(['--conversation_workspace_name', workspaceName,
                             '--common_outputs_workspace', jsonWorkspaceFilename,
                             '--conversation_workspace_id', workspaceId])

        self.t_noExceptionAndLogMessage("Workspace successfully uploaded.", [deployParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        assert len(workspaces) == 1

        # name should be changed accordingly to configuration
        assert workspaces[0]['name'] == workspaceName


    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_nameAndDescriptionNotSet(self, envVarNameUsername, envVarNamePassword):
        """Tests if name and description remains empty."""

        jsonWorkspaceFilename = 'skill_without_name_and_description.json'

        # deploy test workspace with descriptiton and name
        deployParams = list(self.deployParamsBase)
        deployParams.extend(['--common_outputs_workspace', jsonWorkspaceFilename])

        self.t_noExceptionAndLogMessage("Workspace successfully uploaded.", [deployParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        assert len(workspaces) == 1

        assert workspaces[0]['name'] == ""
        assert workspaces[0]['description'] == None


    def test_wrongCredentials(self):
        """Tests if script errors while uploading workspace with wrong credentials."""

        jsonWorkspaceFilename = 'skill_with_name_and_description.json'

        wrongParams = ['--common_outputs_directory', self.dataBasePath,
                             '--common_outputs_workspace', jsonWorkspaceFilename,
                             '--conversation_username', str(uuid.uuid4()),
                             '--conversation_password', str(uuid.uuid4()),
                             '--conversation_url', self.workspacesUrl,
                             '--conversation_version', self.version,
                             '-v']
        self.t_exitCodeAndLogMessage(1, "Unauthorized", [wrongParams])


    def test_args_basic(self):
        ''' Tests some basic sets of args '''

        jsonWorkspaceFilename = 'skill_with_name_and_description.json'

        self.t_unrecognizedArgs([['--nonExistentArg', 'randomNonPositionalArg']])
        # at least one argument (configfile) has to be defined
        self.t_exitCode(1, [[]])
        # check missing required args
        requiredArgsList = ['--common_outputs_directory', self.dataBasePath,
                            '--common_outputs_workspace', jsonWorkspaceFilename,
                            '--conversation_username', str(uuid.uuid4()),
                            '--conversation_password', str(uuid.uuid4()),
                            '--conversation_url', self.workspacesUrl,
                            '--conversation_version', self.version]
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
