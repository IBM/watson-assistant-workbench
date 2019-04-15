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

import json, os, pytest, requests, unittest, uuid

import functions_delete_package
import functions_deploy
from ...test_utils import BaseTestCaseCapture
from urllib.parse import quote
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    packageBase = "Package-for-WAW-CI-"

    def setup_class(cls):
        BaseTestCaseCapture.checkEnvironmentVariables(['CLOUD_FUNCTIONS_USERNAME', 'CLOUD_FUNCTIONS_PASSWORD',
                                                       'CLOUD_FUNCTIONS_NAMESPACE'])
        cls.username = os.environ['CLOUD_FUNCTIONS_USERNAME']
        cls.password = os.environ['CLOUD_FUNCTIONS_PASSWORD']
        cls.apikey = f"{cls.username}:{cls.password}"
        cls.cloudFunctionsUrl = os.environ.get('CLOUD_FUNCTIONS_URL',
                                               'https://us-south.functions.cloud.ibm.com/api/v1/namespaces')
        cls.namespace = os.environ['CLOUD_FUNCTIONS_NAMESPACE']
        cls.urlNamespace = quote(cls.namespace)
        cls.actionsUrl = f"{cls.cloudFunctionsUrl}/{cls.urlNamespace}/actions/"

    def callfunc(self, *args, **kwargs):
        functions_delete_package.main(*args, **kwargs)

    def setup_method(self):
        self.package = self.packageBase + str(uuid.uuid4())

    def teardown_method(self):
        """Delete my package, if it exists."""
        existsResponse = self._getResponseFromPackage()
        if existsResponse.status_code == 200:
            params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctionsEmpty.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl,
                '--cloudfunctions_package', self.package,
                '--cloudfunctions_apikey', self.apikey]
            self.t_noException([params])

    def _getResponseFromPackage(self):
        """Get the package with the name of self.package"""
        packageUrl = f"{self.cloudFunctionsUrl}/{self.urlNamespace}/packages/{self.package}"
        return requests.get(packageUrl, auth=(self.username, self.password), headers={'Content-Type': 'application/json'})

    def _checkPackageExists(self):
        """Check if the package was correctly created"""
        response = self._getResponseFromPackage()
        if response.status_code != 200:
            pytest.fail(f"The package does not exist!")

    def _checkPackageDeleted(self):
        """Check if the package was correctly deleted"""
        response = self._getResponseFromPackage()
        if response.status_code != 404:
            pytest.fail("The package is not deleted!")

    # TODO: Enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_deleteEmptyPackage(self, useApikey):
        """Tests if functions_delete_package deletes uploaded package that is empty."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctionsEmpty.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl,
                '--cloudfunctions_package', self.package]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        functions_deploy.main(params)
        self._checkPackageExists()
        # delete package
        self.t_noException([params])
        self._checkPackageDeleted()

    # TODO: Enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_deleteNonEmptyPackageWithoutSequence(self, useApikey):
        """Tests if functions_delete_package deletes uploaded package that is not empty and doesn't have a sequence."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl,
                '--cloudfunctions_package', self.package]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        functions_deploy.main(params)
        self._checkPackageExists()
        # delete package
        self.t_noException([params])
        self._checkPackageDeleted()

    # TODO: Enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_deleteNonEmptyPackageWithSequence(self, useApikey):
        """Tests if functions_delete_package deletes uploaded package that is not empty and has a sequence."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl]
        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        functions_deploy.main(params)
        self._checkPackageExists()

        sequenceUrl = f"{self.actionsUrl}{self.package}/testSequence"
        functionsDir = os.path.join(self.dataBasePath, 'example_functions')
        functionFileNames = [os.path.basename(os.path.join(functionsDir, f)) for f in os.listdir(functionsDir)]
        # Use fully qualified names!
        functionNames = [f"/{self.namespace}/{self.package}/{os.path.splitext(fileName)[0]}" for fileName in functionFileNames]

        payload = {'exec': {'kind': 'sequence', 'binary': False, 'components': functionNames}}
        # Connect the functions into a sequence
        response = requests.put(sequenceUrl, auth=(self.username, self.password), headers={'Content-Type': 'application/json'},
                                    data=json.dumps(payload), verify=False)

        # Fail if sequence upload failed
        response.raise_for_status()

        # delete package
        self.t_noException([params])
        self._checkPackageDeleted()

    # TODO: Enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_deleteNonexistentPackage(self, useApikey):
        """Tests if functions_delete_package errors while deleting nonexistent package."""

        randomName = str(uuid.uuid4())
        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', randomName, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])
        # Fail
        self.t_exitCodeAndLogMessage(1, "The resource could not be found. Check your cloudfunctions url and namespace.", [params])

    # TODO: Enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_wrongCredentials(self, useApikey):
        """Tests if functions_delete_package errors while deleting with wrong credentials."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl]

        # Correct params for deploy
        paramsDeploy = list(params)
        if useApikey:
            paramsDeploy.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            paramsDeploy.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        # Wrong params for delete
        paramsDelete = list(params)
        randomUsername = str(uuid.uuid4())
        randomPassword = str(uuid.uuid4())
        if useApikey:
            paramsDelete.extend(['--cloudfunctions_apikey', f"{randomUsername}:{randomPassword}"])
        else:
            paramsDelete.extend(['--cloudfunctions_username', randomUsername, '--cloudfunctions_password', randomPassword])

        # Pass
        functions_deploy.main(paramsDeploy)
        self._checkPackageExists()

        # Fail
        self.t_exitCodeAndLogMessage(1, "Authorization error. Check your credentials.", [paramsDelete])

    # TODO: Enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_wrongCloudfunctionsUrl(self, useApikey):
        """Tests if functions_delete_package errors while deleting with wrong cloud functions url."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace]
        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        # Correct params for deploy
        paramsDeploy = list(params)
        paramsDeploy.extend(['--cloudfunctions_url', self.cloudFunctionsUrl])
        # Wrong params for delete
        paramsDelete = list(params)
        paramsDelete.extend(['--cloudfunctions_url', self.cloudFunctionsUrl+str(uuid.uuid4())])

        # Pass
        functions_deploy.main(paramsDeploy)
        self._checkPackageExists()

        # Fail
        self.t_exitCodeAndLogMessage(1,
        "The resource could not be found. Check your cloudfunctions url and namespace.", [paramsDelete])

    # TODO: Enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_wrongNamespace(self, useApikey):
        """Tests if functions_delete_package errors while deleting with wrong namespace."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_url', self.cloudFunctionsUrl]
        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        # Correct params for deploy
        paramsDeploy = list(params)
        paramsDeploy.extend(['--cloudfunctions_namespace', self.urlNamespace])
        # Wrong params for delete
        paramsDelete = list(params)
        paramsDelete.extend(['--cloudfunctions_namespace', self.urlNamespace + self.cloudFunctionsUrl+str(uuid.uuid4())])

        # Pass
        functions_deploy.main(paramsDeploy)
        self._checkPackageExists()

        # Fail
        self.t_exitCodeAndLogMessage(1,
        "The resource could not be found. Check your cloudfunctions url and namespace.", [paramsDelete])
