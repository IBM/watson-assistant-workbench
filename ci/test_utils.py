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

import json, os, pytest, sys, unittest, traceback, shutil

#class BaseTestCaseCapture(unittest.TestCase):
class BaseTestCaseCapture(object):
    '''
    We have two flavours of most of following functions:
    - one with "function" parameter
    - one without function parameter (predefined by "callfunc")
    We can not merge it to one because
    - we want "function" parameter to be positional because if it would be keyword param,
     it would have to be after all positional args
        - do not want positinal argument "kwargs" (and other not frequently used params) to be before it
        - do not want "args" and "kwargs" to be keyword param (function call would be very long)
    - if it would be merged to one function and "function" parameter would be positional,
     we would have to write "None" everytime we want to skip the "function" param (when it is predefined by "callfunc")
        (using "function=None" would not help, this will not skip "function" parameter)
    We also do not want to use different classes for this because it would overcomplicate the code.
    '''

    dialogSchemaPath = '../data_spec/dialog_schema.xml'
    captured = None
    logs = None

    class MessageType(object):
        OUT = 0
        ERR = 1
        LOG = 2

    def t_tooFewArgs(self, args=[], kwargs={}):
        ''' Runs predefined function (callfunc) with given arguments and tests if it fails and error message contains \'too few arguments\' '''
        self.t_fun_tooFewArgs(self.callfunc, args, kwargs)

    def t_fun_tooFewArgs(self, function, args=[], kwargs={}):
        ''' Runs function with given arguments and tests if it fails and error message contains \'too few arguments\' '''
        self.t_fun_exitCodeAndErrMessage(function, 2, 'too few arguments', args, kwargs)

    def t_unrecognizedArgs(self, args=[], kwargs={}):
        ''' Runs predefined function (callfunc) with given arguments and tests if it fails and error message contains \'unrecognized arguments\' '''
        self.t_fun_unrecognizedArgs(self.callfunc, args, kwargs)

    def t_fun_unrecognizedArgs(self, function, args=[], kwargs={}):
        ''' Runs function with given arguments and tests if it fails and error message contains \'unrecognized arguments\' '''
        self.t_fun_exitCodeAndErrMessage(function, 2, 'unrecognized arguments', args, kwargs)

    def t_exitCode(self, exitCode, args=[], kwargs={}):
        ''' Runs predefined function (callfunc) with given arguments and tests exit code '''
        self.t_fun_exitCode(self.callfunc, exitCode, args, kwargs)

    def t_fun_exitCode(self, function, exitCode, args=[], kwargs={}):
        ''' Runs function with given arguments and tests exit code '''
        self.t_fun_exitCodeAndErrMessage(function, exitCode, '', args, kwargs)

    def t_exitCodeAndOutMessage(self, exitCode, outMessage, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exit code and output message '''
        self.t_fun_exitCodeAndOutMessage(self.callfunc, exitCode, outMessage, args, kwargs)

    def t_fun_exitCodeAndOutMessage(self, function, exitCode, outMessage, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exit code and output message '''
        self.t_fun_exitCodeAndMessage(function, exitCode, BaseTestCaseCapture.MessageType.OUT, outMessage, args, kwargs)

    def t_exitCodeAndErrMessage(self, exitCode, errMessage, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exit code and error message '''
        self.t_fun_exitCodeAndErrMessage(self.callfunc, exitCode, errMessage, args, kwargs)

    def t_fun_exitCodeAndErrMessage(self, function, exitCode, errMessage, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exit code and error message '''
        self.t_fun_exitCodeAndMessage(function, exitCode, BaseTestCaseCapture.MessageType.ERR, errMessage, args, kwargs)

    def t_exitCodeAndLogMessage(self, exitCode, logMessage, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exit code and log message '''
        self.t_fun_exitCodeAndLogMessage(self.callfunc, exitCode, logMessage, args, kwargs)

    def t_fun_exitCodeAndLogMessage(self, function, exitCode, logMessage, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exit code and log message '''
        self.t_fun_exitCodeAndMessage(function, exitCode, BaseTestCaseCapture.MessageType.LOG, logMessage, args, kwargs)

    def t_exitCodeAndMessage(self, function, exitCode, messageType, logMessage, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exit code and message of given type '''
        self.t_fun_exitCodeAndMessage(self.callfunc, exitCode, messageType, logMessage, args, kwargs)

    def t_fun_exitCodeAndMessage(self, function, exitCode, messageType, logMessage, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exit code and message of given type '''
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            function(*args, **kwargs)
        self.captured = self.capfd.readouterr()
        self.logs = self.caplog
        assert pytest_wrapped_e.value.code == exitCode

        if messageType == BaseTestCaseCapture.MessageType.OUT:
            assert logMessage in self.captured.out
        elif messageType == BaseTestCaseCapture.MessageType.ERR:
            assert logMessage in self.captured.err
        elif messageType == BaseTestCaseCapture.MessageType.LOG:
            assert logMessage in self.logs.text
        else:
            pytest.fail('Uknown MessageType: ' + messageType)

    def t_raiseError(self, errorType, errMessage, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exception '''
        self.t_fun_raiseError(self.callfunc, errorType, errMessage, args, kwargs)

    def t_fun_raiseError(self, function, errorType, errMessage, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exception '''
        with pytest.raises(errorType, match=errMessage) as pytest_wrapped_e:
            function(*args, **kwargs)
        self.captured = self.capfd.readouterr()
        self.logs = self.caplog

    def t_noException(self, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and checks that no exception was raised '''
        self.t_fun_noException(self.callfunc, args, kwargs)

    def t_fun_noException(self, function, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and checks that no exception was raised '''
        try:
            function(*args, **kwargs)
            self.captured = self.capfd.readouterr()
            self.logs = self.caplog
        except Exception as e:
            pytest.fail(traceback.print_exception(sys.exc_info()))

    def callfunc(self, args=[], kwargs={}):
        ''' (Need to be overidden) Function to be called and tested '''
        raise NotImplementedError()

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    @staticmethod
    def createFolder(folderPath, deleteExisting=True):
        ''' Creates folder with parent folders given by path if the folder does not exist '''
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        elif deleteExisting:
            shutil.rmtree(folderPath)
            os.makedirs(folderPath)

    @staticmethod
    def createFolders(folderPaths, deleteExisting=True):
        ''' Calls createFolder method for each folder path (given by array) '''
        for folderPath in folderPaths:
            BaseTestCaseCapture.createFolder(folderPath, deleteExisting)

    @staticmethod
    def checkEnvironmentVariable(environmentVariable):
        BaseTestCaseCapture.checkEnvironmentVariables([environmentVariable])

    @staticmethod
    def checkEnvironmentVariables(environmentVariables):
        missingEnvironmentVariables = list(set(environmentVariables) - set(os.environ))
        if missingEnvironmentVariables:
            if len(missingEnvironmentVariables) == 1:
                pytest.fail('Missing ENVIRONMENT VARIABLE: ' + missingEnvironmentVariables[0])
            else:
                missingEnvironmentVariables.sort()
                pytest.fail('Missing ENVIRONMENT VARIABLES: ' + str(missingEnvironmentVariables))

