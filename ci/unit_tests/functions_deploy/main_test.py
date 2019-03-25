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

import json, os, requests, shutil, unittest, urllib, uuid, zipfile

import functions_deploy
from ...test_utils import BaseTestCaseCapture

class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    packageBase = "Package-for-WAW-CI-"

    def setup_class(cls):
        BaseTestCaseCapture.checkEnvironmentVariables(['CLOUD_FUNCTIONS_USERNAME', 'CLOUD_FUNCTIONS_PASSWORD',
                                                       'CLOUD_FUNCTIONS_NAMESPACE'])
        cls.username = os.environ['CLOUD_FUNCTIONS_USERNAME']
        cls.password = os.environ['CLOUD_FUNCTIONS_PASSWORD']
        cls.cloudFunctionsUrl = os.environ.get('CLOUD_FUNCTIONS_URL',
                                               'https://us-south.functions.cloud.ibm.com/api/v1/namespaces')
        cls.namespace = os.environ['CLOUD_FUNCTIONS_NAMESPACE']
        cls.urlNamespace = urllib.quote(cls.namespace)

    def callfunc(self, *args, **kwargs):
        functions_deploy.main(*args, **kwargs)

    def _getFunctionsInPackage(self, package):
        functionListUrl = self.cloudFunctionsUrl + '/' + self.urlNamespace + '/actions/?limit=0&skip=0'

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
            # get all functions in package and remove them
            functionNames = self._getFunctionsInPackage(self.package)
            for functionName in functionNames:
                functionDelUrl =  self.cloudFunctionsUrl + '/' + self.urlNamespace + '/actions/' + self.package + \
                    '/' + functionName

                functionDelResp = requests.delete(functionDelUrl, auth=(self.username, self.password))
                assert functionDelResp.status_code == 200

            # remove cloud function package
            packageDelUrl = self.cloudFunctionsUrl + '/' + self.urlNamespace + '/packages/' + self.package

            packageDelResp = requests.delete(packageDelUrl, auth=(self.username, self.password))
            assert packageDelResp.status_code == 200


    def test_functionsUploadFromDirectory(self):
        """Tests if functions_deploy uploads all supported functions from given directory."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                  '--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password,
                  '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                  '--cloudfunctions_url', self.cloudFunctionsUrl]

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
            functionCallUrl = self.cloudFunctionsUrl + '/' + self.urlNamespace + '/actions/' + self.package + \
                '/' + functionName + '?blocking=true&result=true'

            functionResp = requests.post(functionCallUrl, auth=(self.username, self.password),
                                         headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                                         data=json.dumps({'name': 'unit test'}))

            assert functionResp.status_code == 200
            functionRespJson = functionResp.json()
            assert "Hello unit test!" in functionRespJson['greeting']


    def test_pythonVersionFunctions(self):
        """Tests if it's possible to upload one fuction into two different version of runtime."""
        for pythonVersion in [2, 3]:
            params = ['-c', os.path.join(self.dataBasePath, 'python' + str(pythonVersion) + 'Functions.cfg'),
                      '--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password,
                      '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                      '--cloudfunctions_url', self.cloudFunctionsUrl]

            self.t_noException([params])
            self.packageCreated = True

            functionCallUrl = self.cloudFunctionsUrl + '/' + self.urlNamespace + '/actions/' + self.package + \
                '/getPythonMajorVersion?blocking=true&result=true'

            functionResp = requests.post(functionCallUrl, auth=(self.username, self.password),
                                         headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                                         data="{}")

            assert functionResp.status_code == 200
            functionRespJson = functionResp.json()
            assert pythonVersion == functionRespJson['majorVersion']


    def test_functionsInZip(self):
        """Tests if functions_deploy can handle function in zip file."""
        # prepare zip file
        dirForZip = os.path.join(self.dataBasePath, "outputs", "pythonZip")
        BaseTestCaseCapture.createFolder(dirForZip)

        with zipfile.ZipFile(os.path.join(dirForZip, 'testFunc.zip'), 'w') as functionsZip:
            for fileToZip in os.listdir(os.path.join(self.dataBasePath, 'zip_functions')):
                functionsZip.write(os.path.join(self.dataBasePath, 'zip_functions', fileToZip), fileToZip)

        #upload zip file
        params = ['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password,
                  '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                  '--cloudfunctions_url', self.cloudFunctionsUrl, '--common_functions', [dirForZip]]

        self.t_noException([params])
        self.packageCreated = True

        # call function and check if sub-function from non-main file was called
        functionCallUrl = self.cloudFunctionsUrl + '/' + self.urlNamespace + '/actions/' + self.package + \
            '/testFunc?blocking=true&result=true'

        functionResp = requests.post(functionCallUrl, auth=(self.username, self.password),
                                     headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                                     data="{}")

        assert functionResp.status_code == 200
        functionRespJson = functionResp.json()
        assert "String from helper function" == functionRespJson['test']


    def test_badArgs(self):
        """Tests some basic common problems with args."""
        self.t_unrecognizedArgs([['--nonExistentArg', 'randomNonPositionalArg']])
        self.t_exitCode(1, [[]])

        completeArgsList = ['--cloudfunctions_username', self.username,
                            '--cloudfunctions_password', self.password,
                            '--cloudfunctions_package', self.package,
                            '--cloudfunctions_namespace', self.urlNamespace,
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

            self.t_exitCodeAndLogMessage(1, paramName, [argsListWithoutOne])
