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

import json, os, requests, unittest, urllib, uuid

import functions_deploy
from .. import unit_utils

class TestMain(unit_utils.BaseTestCaseCapture):

    dataBasePath = "./ci/unit_tests/functions_deploy/main_data/"
    namespace = "Prague Cognitive Services_IoT-Prague"
    urlNamespace = urllib.quote(namespace)
    packageBase = "Package-for-WAW-CI-"

    def callfunc(self, *args, **kwargs):
        functions_deploy.main(*args, **kwargs)

    def _getFunctionsInPackage(self, package):
        functionListUrl = 'https://us-south.functions.cloud.ibm.com/api/v1/namespaces/' + self.urlNamespace + \
            '/actions/?limit=0&skip=0'

        functionListResp = requests.get(functionListUrl, auth=(os.environ['CLOUD_FUNCTIONS_USERNAME'],
                                                               os.environ['CLOUD_FUNCTIONS_PASSWORD']),
                                        headers={'accept': 'application/json'})

        assert functionListResp.status_code == 200

        functionListJson = functionListResp.json()
        functionNames = []

        for function in functionListJson:
            if (self.namespace + '/' + package) in function['namespace']:
                functionNames += [function['name']]

        return functionNames


    def setUp(self):
        self.package = self.packageBase + str(uuid.uuid4())
        self.packageCreated = False # test should set that to true if it created package for cloud functions

    def tearDown(self):
        if self.packageCreated:
            # get all functions in package and remove them
            functionNames = self._getFunctionsInPackage(self.package)
            for functionName in functionNames:
                functionDelUrl = 'https://us-south.functions.cloud.ibm.com/api/v1/namespaces/' + self.urlNamespace + \
                    '/actions/' + self.package + '/' + functionName

                functionDelResp = requests.delete(functionDelUrl, auth=(os.environ['CLOUD_FUNCTIONS_USERNAME'],
                                                                        os.environ['CLOUD_FUNCTIONS_PASSWORD']))
                assert functionDelResp.status_code == 200

            # remove cloud function package
            packageDelUrl = 'https://us-south.functions.cloud.ibm.com/api/v1/namespaces/' + self.urlNamespace + \
                '/packages/' + self.package

            packageDelResp = requests.delete(packageDelUrl, auth=(os.environ['CLOUD_FUNCTIONS_USERNAME'],
                                                                  os.environ['CLOUD_FUNCTIONS_PASSWORD']))
            assert packageDelResp.status_code == 200


    def test_functionsUploadFromDirectory(self):
        """Tests if functions_deploy uploads all supported functions from given directory."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                  '--cloudfunctions_username', os.environ['CLOUD_FUNCTIONS_USERNAME'],
                  '--cloudfunctions_password', os.environ['CLOUD_FUNCTIONS_PASSWORD'],
                  '--cloudfunctions_package', self.package]

        # upload functions
        functions_deploy.main(params)
        self.packageCreated = True

        # obtain list of uploaded functions
        functionNames = self._getFunctionsInPackage(self.package)

        # get original list of cloud function files and check if all of them were uploaded
        functionsDir = os.path.join(self.dataBasePath, 'example_functions')
        functionFileNames = [os.path.splitext(fileName)[0] for fileName in os.listdir(functionsDir)]
        assert set(functionNames) == set(functionFileNames)

        # try to call particular functions
        for functionName in functionNames:
            functionCallUrl = 'https://us-south.functions.cloud.ibm.com/api/v1/namespaces/' + self.urlNamespace + \
                '/actions/' + self.package + '/' + functionName + '?blocking=true&result=true'

            functionResp = requests.post(functionCallUrl, auth=(os.environ['CLOUD_FUNCTIONS_USERNAME'],
                                                                os.environ['CLOUD_FUNCTIONS_PASSWORD']),
                                         headers={'Content-Type': 'application/json',
                                                  'accept': 'application/json'},
                                         data=json.dumps({'name': 'unit test'}))

            assert functionResp.status_code == 200
            functionRespJson = functionResp.json()
            assert "Hello unit test!" in functionRespJson['greeting']


    def test_pythonVersionFunctions(self):
        """Tests if it's possible to upload one fuction into two different version of runtime."""
        for pythonVersion in [2, 3]:
            params = ['-c', os.path.join(self.dataBasePath, 'python' + str(pythonVersion) + 'Functions.cfg'),
                      '--cloudfunctions_username', os.environ['CLOUD_FUNCTIONS_USERNAME'],
                      '--cloudfunctions_password', os.environ['CLOUD_FUNCTIONS_PASSWORD'],
                      '--cloudfunctions_package', self.package]

            functions_deploy.main(params)
            self.packageCreated = True

            functionCallUrl = 'https://us-south.functions.cloud.ibm.com/api/v1/namespaces/' + self.urlNamespace + \
                '/actions/' + self.package + '/getPythonMajorVersion?blocking=true&result=true'

            functionResp = requests.post(functionCallUrl, auth=(os.environ['CLOUD_FUNCTIONS_USERNAME'],
                                                                os.environ['CLOUD_FUNCTIONS_PASSWORD']),
                                         headers={'Content-Type': 'application/json',
                                                  'accept': 'application/json'},
                                         data="{}")

            assert functionResp.status_code == 200
            functionRespJson = functionResp.json()
            assert pythonVersion == functionRespJson['majorVersion']

    def test_badArgs(self):
        ''' Tests some basic common problems with args'''
        self.tUnrecognizedArgs(['--nonExistentArg', 'randomNonPositionalArg'])
        self.tExitCode(1, [])

        completeArgsList = ['--cloudfunctions_username', os.environ['CLOUD_FUNCTIONS_USERNAME'],
                            '--cloudfunctions_password', os.environ['CLOUD_FUNCTIONS_PASSWORD'],
                            '--cloudfunctions_package', self.package,
                            '--cloudfunctions_namespace', self.urlNamespace,
                            '--common_functions', self.dataBasePath]

        for argIndex in range(len(completeArgsList)):
            if not completeArgsList[argIndex].startswith('--'):
                continue
            paramName = completeArgsList[argIndex][2:]

            missingArgsList = []
            for i in range(len(completeArgsList)):
                if i != argIndex and i != (argIndex + 1):
                    missingArgsList += [completeArgsList[i]]

            self.tExitCodeAndErrMessage(1, paramName, missingArgsList)
