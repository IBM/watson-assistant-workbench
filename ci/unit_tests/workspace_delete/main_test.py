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

import argparse
import os
import uuid

import pytest
import requests

import workspace_delete
import workspace_deploy
from cfgCommons import Cfg
from wawCommons import getRequiredParameter, getWorkspaces

from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    outputPath = os.path.join(dataBasePath, 'outputs')
    jsonWorkspaceFilename = 'sample-skill.json'
    jsonWorkspacePath = os.path.abspath(os.path.join(dataBasePath, jsonWorkspaceFilename))
    workspacesUrl = os.environ['WA_URL']
    version = os.environ['WA_VERSION']

    def setup_class(cls):
        BaseTestCaseCapture.createFolder(cls.outputPath)
        BaseTestCaseCapture.checkEnvironmentVariables(['WA_USERNAME', 'WA_PASSWORD'])
        cls.username = os.environ['WA_USERNAME']
        cls.password = os.environ['WA_PASSWORD']

        cls.deployParamsBase = ['--common_outputs_directory', cls.dataBasePath,
                                '--common_outputs_workspace', cls.jsonWorkspaceFilename,
                                '--conversation_username', cls.username,
                                '--conversation_password', cls.password,
                                '--conversation_url', cls.workspacesUrl,
                                '--conversation_version', cls.version,
                                '-v']

        cls.deleteParamsBase = ['--conversation_username', cls.username,
                                '--conversation_password', cls.password,
                                '--conversation_url', cls.workspacesUrl,
                                '--conversation_version', cls.version,
                                '-v']

    def callfunc(self, *args, **kwargs):
        workspace_delete.main(*args, **kwargs)

    def setup_method(self):
        self._deleteAllWorkspaces()

    def teardown_method(self):
        self._deleteAllWorkspaces()

    def _deleteAllWorkspaces(self):

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        for workspace in workspaces:
            requestUrl = self.workspacesUrl + '/' + workspace['workspace_id'] + '?version=' + self.version
            requests.delete(requestUrl, auth=(self.username, self.password), headers={'Accept': 'text/html'})

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        assert len(workspaces) == 0

    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_deleteById(self, envVarNameUsername, envVarNamePassword):
        """Tests if workspace can be deleted by its id."""

        # use outputPath instead of dataBasePath when workspace_deploy script will be able to take workspace
        # and config file from different directories (workspace should be taken from
        # dataBasePath and config should be saved to outputs directory)
        createOutputConfigFilename = 'createWorkspaceOutput.cfg'
        createOutputConfigPath = os.path.abspath(os.path.join(self.dataBasePath, createOutputConfigFilename))
        deleteOutputConfigFilename = 'deleteWorkspaceOutput.cfg'
        deleteOutputConfigPath = os.path.abspath(os.path.join(self.dataBasePath, deleteOutputConfigFilename))

        workspaceName = 'deleteById_workspace'

        # deploy test workspace
        deployParams = list(self.deployParamsBase)
        deployParams.extend(['--common_output_config', createOutputConfigPath,
                             '--conversation_workspace_name', workspaceName])
        workspace_deploy.main(deployParams)
        # deploy one more workspace
        deployParamsMore = list(self.deployParamsBase)
        deployParamsMore.extend(['--conversation_workspace_name', workspaceName])
        workspace_deploy.main(deployParamsMore)

        # try to delete workspace by its id (id is obtained from output config of deploy script)
        deleteParams = list(self.deleteParamsBase)
        deleteParams.extend(['-c', createOutputConfigPath,
                             '--common_output_config', deleteOutputConfigPath])
        self.t_noExceptionAndLogMessage("One workspace has been successfully deleted",[deleteParams])

        # parse output config of deploy script (contains workspace id to delete)
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
        args = parser.parse_args(['--common_configFilePaths', createOutputConfigPath])
        createOutputConfig = Cfg(args)

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        # in workspaces on server there should be no workspace with id from config file
        workspacesFound = 0
        for workspace in workspaces:
            if workspace['workspace_id'] == getRequiredParameter(createOutputConfig, 'conversation_workspace_id'):
                workspacesFound += 1

        assert workspacesFound == 0

        # there should be still one workspace left (even with the same name)
        assert len(workspaces) == 1

        # check if workspace_id is not present in the output config of delete script
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
        args = parser.parse_args(['--common_configFilePaths', deleteOutputConfigPath])
        deleteOutputConfig = Cfg(args)

        assert hasattr(deleteOutputConfig, 'conversation_workspace_id') == False

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_deleteMoreByName(self, envVarNameUsername, envVarNamePassword):
        """Tests if more workspaces with the same name can be deleted by their name."""

        workspaceName = 'deleteByName_workspace'
        workspaceNameNM = 'non-matching_workspace'

        # deploy test workspace
        deployParams = list(self.deployParamsBase)
        deployParams.extend(['--conversation_workspace_name', workspaceName])
        workspace_deploy.main(deployParams)
        # deploy second workspace with the same name
        workspace_deploy.main(deployParams)
        # deploy non-matching workspace
        deployParamsNM = list(self.deployParamsBase)
        deployParamsNM.extend(['--conversation_workspace_name', workspaceNameNM])
        workspace_deploy.main(deployParamsNM)

        # try to delete workspace by its name
        deleteParams = list(self.deleteParamsBase)
        deleteParams.extend(['--conversation_workspace_name', workspaceName,
                             '--conversation_workspace_match_by_name', 'true'])
        self.t_noExceptionAndLogMessage("2 workspaces have been successfully deleted",[deleteParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        # there should be no workspace with specified name in config file
        workspacesFound = 0
        for workspace in workspaces:
            if workspace['name'] == workspaceName:
                workspacesFound += 1

        assert workspacesFound == 0

        # there should be still workspace with non-matching name
        assert len(workspaces) == 1

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_deleteMoreWithRegexp(self, envVarNameUsername, envVarNamePassword):
        """Tests if more workspaces can be deleted by regular expression."""

        workspaceName1 = 'regexp_workspace_1'
        workspaceName2 = 'regexp_workspace_2'
        workspaceNameNM = 'non-matching_workspace'

        # deploy test workspaces
        deployParams1 = list(self.deployParamsBase)
        deployParams1.extend(['--conversation_workspace_name', workspaceName1])
        workspace_deploy.main(deployParams1)
        # deploy second workspace with matching name
        deployParams2 = list(self.deployParamsBase)
        deployParams2.extend(['--conversation_workspace_name', workspaceName2])
        workspace_deploy.main(deployParams2)
        # deploy non-matching workspace
        deployParamsNM = list(self.deployParamsBase)
        deployParamsNM.extend(['--conversation_workspace_name', workspaceNameNM])
        workspace_deploy.main(deployParamsNM)

        # try to delete workspace by regular expression
        deleteParams = list(self.deleteParamsBase)
        deleteParams.extend(['--conversation_workspace_match_by_name', 'true',
                             '--conversation_workspace_name_pattern', 'regexp_*'])
        self.t_noExceptionAndLogMessage("2 workspaces have been successfully deleted",[deleteParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        # there should be no workspace with name matching specified regex
        workspacesFound = 0
        for workspace in workspaces:
            if workspace['name'] == workspaceName1 or workspace['name'] == workspaceName2:
                workspacesFound += 1

        assert workspacesFound == 0

        # there should be still workspace with non-matching name
        assert len(workspaces) == 1

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_deleteAllWithRegex(self, envVarNameUsername, envVarNamePassword):
        """Tests if all workspaces can be deleted by '*'."""

        workspaceName1 = "workspace-1?"
        workspaceName2 = "Šťastný s'kill"
        workspaceName3 = "My skill"

        # deploy test workspaces
        deployParams1 = list(self.deployParamsBase)
        deployParams1.extend(['--conversation_workspace_name', workspaceName1])
        workspace_deploy.main(deployParams1)

        deployParams2 = list(self.deployParamsBase)
        deployParams2.extend(['--conversation_workspace_name', workspaceName2])
        workspace_deploy.main(deployParams2)

        deployParams3 = list(self.deployParamsBase)
        deployParams3.extend(['--conversation_workspace_name', workspaceName3])
        workspace_deploy.main(deployParams3)

        # try to delete all workspaces
        deleteParams = list(self.deleteParamsBase)
        deleteParams.extend(['--conversation_workspace_match_by_name', 'true',
                             '--conversation_workspace_name_pattern', '.*'])
        self.t_noExceptionAndLogMessage("3 workspaces have been successfully deleted",[deleteParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        # there should be no workspace left
        assert len(workspaces) == 0

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_deleteByNameNoneMatching(self, envVarNameUsername, envVarNamePassword):
        """Tests if no workspace matches name."""

        # non matching workspace
        workspaceName = "My skill"
        deployParams = list(self.deployParamsBase)
        deployParams.extend(['--conversation_workspace_name', workspaceName])
        workspace_deploy.main(deployParams)

        # try to delete non-matching workspace
        deleteParams = list(self.deleteParamsBase)
        deleteParams.extend(['--conversation_workspace_match_by_name', 'true',
                             '--conversation_workspace_name_pattern', 'workspace'])
        self.t_noExceptionAndLogMessage("No workspace has been deleted",[deleteParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        # there should be still one workspace left
        assert len(workspaces) == 1

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_deleteFromEmpty(self, envVarNameUsername, envVarNamePassword):
        """Tests if it wont fail when no workspace is present."""

        # try to delete all workspaces
        deleteParams = list(self.deleteParamsBase)
        deleteParams.extend(['--conversation_workspace_match_by_name', 'true',
                             '--conversation_workspace_name_pattern', 'workspace'])
        self.t_noExceptionAndLogMessage("No workspace has been deleted",[deleteParams])

    def test_wrongCredentials(self):
        """Tests if script errors while deleting with wrong credentials."""

        # Wrong params for delete
        wrongParamsDelete = ['--conversation_username', str(uuid.uuid4()),
                                '--conversation_password', str(uuid.uuid4()),
                                '--conversation_url', self.workspacesUrl,
                                '--conversation_version', self.version,
                                '-v']
        self.t_exitCodeAndLogMessage(1, "Failed to retrieve workspaces to delete.", [wrongParamsDelete])

    def test_args_basic(self):
        ''' Tests some basic sets of args '''
        self.t_unrecognizedArgs([['--nonExistentArg', 'randomNonPositionalArg']])
        # at least one argument (configfile) has to be defined
        self.t_exitCode(1, [[]])
        # check missing required args
        requiredArgsList = ['--conversation_username', self.username,
                            '--conversation_password', self.password,
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

        # match by name true and neither name nor pattern defined
        conditionalArgsList = list(requiredArgsList)
        conditionalArgsList.extend(['--conversation_workspace_match_by_name', 'true'])
        message = "'conversation_workspace_match_by_name' set to true but neither 'conversation_workspace_name' nor 'conversation_workspace_name_pattern' is defined."
        self.t_exitCodeAndLogMessage(1, message, [conditionalArgsList])
