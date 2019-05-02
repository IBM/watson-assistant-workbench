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

import json, os, pytest, requests, shutil, unittest, uuid, zipfile

import functions_deploy
import functions_delete_package
from ...test_utils import BaseTestCaseCapture
from urllib.parse import quote


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    packageBase = "Package-for-WAW-CI-"

    def setup_class(cls):
        BaseTestCaseCapture.checkEnvironmentVariables(['CLOUD_FUNCTIONS_USERNAME', 'CLOUD_FUNCTIONS_PASSWORD',
                                                       'CLOUD_FUNCTIONS_NAMESPACE'])
        cls.username = os.environ['CLOUD_FUNCTIONS_USERNAME']
        cls.password = os.environ['CLOUD_FUNCTIONS_PASSWORD']
        cls.apikey = cls.username + ':' + cls.password
        cls.cloudFunctionsUrl = os.environ.get('CLOUD_FUNCTIONS_URL',
                                               'https://us-south.functions.cloud.ibm.com/api/v1/namespaces')
        cls.namespace = os.environ['CLOUD_FUNCTIONS_NAMESPACE']
        cls.urlNamespace = quote(cls.namespace)
        cls.actionsUrl = cls.cloudFunctionsUrl + '/' + cls.urlNamespace + '/actions/'

    def callfunc(self, *args, **kwargs):
        functions_deploy.main(*args, **kwargs)

    def _getFunctionsInPackage(self, package):
        functionListUrl = self.actionsUrl + '?limit=0&skip=0'
        functionListResp = requests.get(functionListUrl, auth=(self.username, self.password),
                                        headers={'accept': 'application/json'})

        assert functionListResp.status_code == 200

        functionListJson = functionListResp.json()
        functionNames = []

        for function in functionListJson:
            if (self.namespace + '/' + package) in function['namespace']:
                functionNames.append(function['name'])

        return functionNames


    def setup_method(self):
        self.package = self.packageBase + str(uuid.uuid4())
        self.packageCreated = False # test should set that to true if it created package for cloud functions

    def teardown_method(self):
        if self.packageCreated:
            # Delete the package
            params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.namespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl,
                '--cloudfunctions_package', self.package,
                '--cloudfunctions_apikey', self.apikey]
            self.t_fun_noException(functions_delete_package.main, [params])

    @pytest.mark.parametrize('useApikey', [True, False])
    def test_functionsUploadFromDirectory(self, useApikey):
        """Tests if functions_deploy uploads all supported functions from given directory."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                  '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.namespace,
                  '--cloudfunctions_url', self.cloudFunctionsUrl]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        # upload functions
        self.t_noException([params])
        self.packageCreated = True

        # obtain list of uploaded functions
        functionNames = self._getFunctionsInPackage(self.package)

        # get original list of cloud function files and check if all of them were uploaded
        functionsDir = os.path.join(self.dataBasePath, 'example_functions')
        functionFileNames = [os.path.splitext(fileName)[0] for fileName in os.listdir(functionsDir)]
        assert set(functionNames) == set(functionFileNames)

        # try to call particular functions
        for functionName in functionNames:
            functionCallUrl = self.actionsUrl + self.package + '/' + functionName + '?blocking=true&result=true'

            functionResp = requests.post(functionCallUrl, auth=(self.username, self.password),
                                         headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                                         data=json.dumps({'name': 'unit test'}))

            assert functionResp.status_code == 200
            functionRespJson = functionResp.json()
            assert "Hello unit test!" in functionRespJson['greeting']

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    @pytest.mark.parametrize('useApikey', [True, False])
    def test_pythonVersionFunctions(self, useApikey):
        """Tests if it's possible to upload one function into two different version of runtime."""
        for pythonVersion in [2, 3]:
            params = ['-c', os.path.join(self.dataBasePath, 'python' + str(pythonVersion) + 'Functions.cfg'),
                      '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.namespace,
                      '--cloudfunctions_url', self.cloudFunctionsUrl]

            if useApikey:
                params.extend(['--cloudfunctions_apikey', self.apikey])
            else:
                params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

            self.t_noException([params])
            self.packageCreated = True

            functionCallUrl = self.actionsUrl + self.package + '/getPythonMajorVersion?blocking=true&result=true'

            functionResp = requests.post(functionCallUrl, auth=(self.username, self.password),
                                         headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                                         data="{}")

            assert functionResp.status_code == 200
            functionRespJson = functionResp.json()
            assert pythonVersion == functionRespJson['majorVersion']

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    @pytest.mark.parametrize('useApikey', [True, False])
    def test_functionsInZip(self, useApikey):
        """Tests if functions_deploy can handle function in zip file."""
        # prepare zip file
        dirForZip = os.path.join(self.dataBasePath, "outputs", "pythonZip")
        BaseTestCaseCapture.createFolder(dirForZip)

        with zipfile.ZipFile(os.path.join(dirForZip, 'testFunc.zip'), 'w') as functionsZip:
            for fileToZip in os.listdir(os.path.join(self.dataBasePath, 'zip_functions')):
                functionsZip.write(os.path.join(self.dataBasePath, 'zip_functions', fileToZip), fileToZip)

        #upload zip file
        params = ['--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.namespace,
                  '--cloudfunctions_url', self.cloudFunctionsUrl, '--common_functions', [dirForZip]]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        self.t_noException([params])
        self.packageCreated = True

        # call function and check if sub-function from non-main file was called
        functionCallUrl = self.actionsUrl + self.package + '/testFunc?blocking=true&result=true'

        functionResp = requests.post(functionCallUrl, auth=(self.username, self.password),
                                     headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                                     data="{}")

        assert functionResp.status_code == 200
        functionRespJson = functionResp.json()
        assert "String from helper function" == functionRespJson['test']

    @pytest.mark.parametrize('useApikey', [True, False])
    def test_functionsUploadSequence(self, useApikey):
        """Tests if functions_deploy uploads sequences."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleValidSequences.cfg'),
                  '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.namespace,
                  '--cloudfunctions_url', self.cloudFunctionsUrl]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        # upload functions
        self.t_noException([params])
        self.packageCreated = True

        sequenceAnswers = {"a" : "123", "b" : "231", "c" : "312"}
        # try to call particular sequences and test their output
        for sequenceName in sequenceAnswers:
            sequenceCallUrl = self.actionsUrl + self.package + '/' + sequenceName + '?blocking=true&result=true'

            sequenceResp = requests.post(sequenceCallUrl, auth=(self.username, self.password),
                                         headers={'Content-Type': 'application/json', 'accept': 'application/json'})

            assert sequenceResp.status_code == 200
            sequenceRespJson = sequenceResp.json()
            shouldAnswer = sequenceAnswers[sequenceName]
            assert shouldAnswer in sequenceRespJson["entries"]

    @pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE') != "cron", reason="This test is nightly build only.")
    @pytest.mark.parametrize('useApikey', [True, False])
    def test_functionsMissingSequenceComponent(self, useApikey):
        """Tests if functions_deploy fails when uploading a sequence with a nonexistent function."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleNonexistentFunctionRef.cfg'),
                  '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.namespace,
                  '--cloudfunctions_url', self.cloudFunctionsUrl]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        # upload functions (will fail AFTER package creation)
        self.packageCreated = True
        self.t_exitCodeAndLogMessage(1, "Unexpected error code", [params])

    @pytest.mark.parametrize('useApikey', [True, False])
    def test_functionsMissingSequenceDefinition(self, useApikey):
        """Tests if functions_deploy fails when uploading a sequence without a function list."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleUndefinedSequence.cfg'),
                  '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.namespace,
                  '--cloudfunctions_url', self.cloudFunctionsUrl]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        # Fails before anything is uploaded
        self.t_exitCodeAndLogMessage(1, "parameter not defined", [params])

    def test_badArgs(self):
        """Tests some basic common problems with args."""
        self.t_unrecognizedArgs([['--nonExistentArg', 'randomNonPositionalArg']])
        self.t_exitCode(1, [[]])

        completeArgsList = ['--cloudfunctions_username', self.username,
                            '--cloudfunctions_password', self.password,
                            '--cloudfunctions_apikey', self.password + ":" + self.username,
                            '--cloudfunctions_package', self.package,
                            '--cloudfunctions_namespace', self.namespace,
                            '--cloudfunctions_url', self.cloudFunctionsUrl,
                            '--common_functions', self.dataBasePath]

        for argIndex in range(len(completeArgsList)):
            if not completeArgsList[argIndex].startswith('--'):
                continue
            paramName = completeArgsList[argIndex][2:]

            argsListWithoutOne = []
            for i in range(len(completeArgsList)):
                if i != argIndex and i != (argIndex + 1):
                    argsListWithoutOne.append(completeArgsList[i])

            if paramName in ['cloudfunctions_username', 'cloudfunctions_password']:
                message = 'combination already set: \'[\'cloudfunctions_apikey\']\''
            elif paramName in ['cloudfunctions_apikey']:
                # we have to remove username and password (if not it would be valid combination of parameters)
                argsListWithoutOne = argsListWithoutOne[4:] # remove username and password (leave just apikey)
                message = 'Combination 0: \'cloudfunctions_apikey\''
            else:
                # we have to remove username and password (if not then it would always return error that both auth types are provided)
                argsListWithoutOne = argsListWithoutOne[4:] # remove username and password (leave just apikey)
                message = 'required \'' + paramName + '\' parameter not defined'
            self.t_exitCodeAndLogMessage(1, message, [argsListWithoutOne])
