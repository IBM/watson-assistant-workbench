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

import os, pytest, unittest

class BaseTestCaseCapture(unittest.TestCase):

    def tTooFewArgs(self, *args, **kwargs):
        ''' Runs function with given arguments and tests if it fails and error message contains \'too few arguments\' '''
        self.tExitCodeAndErrMessage(2, 'too few arguments', *args, **kwargs)

    def tUnrecognizedArgs(self, *args, **kwargs):
        ''' Runs function with given arguments and tests if it fails and error message contains \'unrecognized arguments\' '''
        self.tExitCodeAndErrMessage(2, 'unrecognized arguments', *args, **kwargs)

    def tExitCode(self, exitCode, *args, **kwargs):
        ''' Runs function with given arguments and tests exit code '''
        self.tExitCodeAndErrMessage(exitCode, '', *args, **kwargs)

    def tExitCodeAndErrMessage(self, exitCode, errMessage, *args, **kwargs):
        ''' (Generic) Runs function with given arguments and tests exit code and error message '''
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            self.callfunc(*args, **kwargs)
        captured = self.capfd.readouterr()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == exitCode
        assert errMessage in captured.err

    def tRaiseError(self, errorType, errMessage, *args, **kwargs):
        ''' (Generic) Runs function with given arguments and tests exception '''
        with pytest.raises(errorType) as pytest_wrapped_e:
            self.callfunc(*args, **kwargs)
        captured = self.capfd.readouterr()
        assert pytest_wrapped_e.type == errorType
        assert errMessage in pytest_wrapped_e.value

    def callfunc(self, *args, **kwargs):
        ''' (Need to be overidden) Function to be called and tested '''
        raise NotImplementedError()

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

