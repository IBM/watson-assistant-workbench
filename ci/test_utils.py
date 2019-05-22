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

import os
import shutil
import traceback

import pytest


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

    def t_missingRequiredArgs(self, args=[], kwargs={}):
        ''' Runs predefined function (callfunc) with given arguments and tests if it fails and error message contains \'the following arguments are required\' '''
        self.t_fun_missingRequiredArgs(self.callfunc, args, kwargs)

    def t_fun_missingRequiredArgs(self, function, args=[], kwargs={}):
        ''' Runs function with given arguments and tests if it fails and error message contains \'the following arguments are required\' '''
        self.t_fun_exitCodeAndErrMessage(function, 2, 'the following arguments are required', args, kwargs)

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
        self.t_fun_exitCodeAndMessage(function, exitCode, None, None, args, kwargs)

    def t_exitCodeAndOutMessage(self, exitCode, message, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exit code and output message '''
        self.t_fun_exitCodeAndOutMessage(self.callfunc, exitCode, message, args, kwargs)

    def t_fun_exitCodeAndOutMessage(self, function, exitCode, message, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exit code and output message '''
        self.t_fun_exitCodeAndMessage(function, exitCode, BaseTestCaseCapture.MessageType.OUT, message, args, kwargs)

    def t_exitCodeAndErrMessage(self, exitCode, errMessage, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exit code and error message '''
        self.t_fun_exitCodeAndErrMessage(self.callfunc, exitCode, errMessage, args, kwargs)

    def t_fun_exitCodeAndErrMessage(self, function, exitCode, errMessage, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exit code and error message '''
        self.t_fun_exitCodeAndMessage(function, exitCode, BaseTestCaseCapture.MessageType.ERR, errMessage, args, kwargs)

    def t_exitCodeAndLogMessage(self, exitCode, message, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exit code and log message '''
        self.t_fun_exitCodeAndLogMessage(self.callfunc, exitCode, message, args, kwargs)

    def t_fun_exitCodeAndLogMessage(self, function, exitCode, message, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exit code and log message '''
        self.t_fun_exitCodeAndMessage(function, exitCode, BaseTestCaseCapture.MessageType.LOG, message, args, kwargs)

    def t_exitCodeAndMessage(self, function, exitCode, messageType, message, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exit code and message of given type '''
        self.t_fun_exitCodeAndMessage(self.callfunc, exitCode, messageType, message, args, kwargs)

    def t_fun_exitCodeAndMessage(self, function, exitCode, messageType, message, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exit code and message of given type '''
        self.t_fun_generic(function, SystemExit, str(exitCode), messageType, message, args, kwargs)

    def t_raiseException(self, exceptionType, exceptionValue, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exception '''
        self.t_fun_raiseException(self.callfunc, exceptionType, exceptionValue, args, kwargs)

    def t_fun_raiseException(self, function, exceptionType, exceptionValue, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests exception '''
        self.t_fun_generic(function, exceptionType, exceptionValue, None, None, args, kwargs)

    def t_noException(self, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and checks that no exception was raised '''
        self.t_fun_noException(self.callfunc, args, kwargs)

    def t_fun_noException(self, function, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and checks that no exception was raised '''
        self.t_fun_noExceptionAndMessage(function, None, None, args, kwargs)

    def t_noExceptionAndOutMessage(self, message, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and checks that no exception was raised and output message '''
        self.t_fun_noExceptionAndOutMessage(self.callfunc, message, args, kwargs)

    def t_fun_noExceptionAndOutMessage(self, function, message, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and checks that no exception was raised and output message '''
        self.t_fun_noExceptionAndMessage(function, BaseTestCaseCapture.MessageType.OUT, message, args, kwargs)

    def t_noExceptionAndErrMessage(self, message, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and checks that no exception was raised and error message '''
        self.t_fun_noExceptionAndErrMessage(self.callfunc, message, args, kwargs)

    def t_fun_noExceptionAndErrMessage(self, function, message, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tchecks that no exception was raised and error message '''
        self.t_fun_noExceptionAndMessage(function, BaseTestCaseCapture.MessageType.ERR, message, args, kwargs)

    def t_noExceptionAndLogMessage(self, message, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and checks that no exception was raised and log message '''
        self.t_fun_noExceptionAndLogMessage(self.callfunc, message, args, kwargs)

    def t_fun_noExceptionAndLogMessage(self, function, message, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and checks that no exception was raised and log message '''
        self.t_fun_noExceptionAndMessage(function, BaseTestCaseCapture.MessageType.LOG, message, args, kwargs)

    def t_noExceptionAndMessage(self, messageType, message, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and checks that no exception was raised and message of given type '''
        self.t_fun_noExceptionAndMessage(self.callfunc, messageType, message, args, kwargs)

    def t_fun_noExceptionAndMessage(self, function, messageType, message, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and checks that no exception was raised and message of given type '''
        self.t_fun_generic(function, None, None, messageType, message, args, kwargs)

    def t_generic(self, exceptionType, exceptionValue, messageType, message, args=[], kwargs={}):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests if everything is set as should be '''
        self.t_fun_generic(self.callfunc, exceptionType, exceptionValue, messageType, message, args, kwargs)

    def t_fun_generic(self, function, exceptionType, exceptionValue, messageType, message, args=[], kwargs={}):
        ''' (Generic) Runs function with given arguments and tests if everything is set as should be '''
        exception = None

        try:
            function(*args, **kwargs)
        except BaseException as e:
            exception = e
            if not exceptionType:
                pytest.fail(traceback.format_exc())

        if exceptionType:
            assert exceptionType == type(exception), "Exception: " + str(exception)
        else:
            assert exception == None

        if exceptionValue:
            assert exceptionValue in str(exception)
        else:
            assert exception == None

        self.captured = self.capfd.readouterr()
        self.logs = self.caplog
        if messageType:
            if messageType == BaseTestCaseCapture.MessageType.OUT:
                assert message in self.captured.out
            elif messageType == BaseTestCaseCapture.MessageType.ERR:
                assert message in self.captured.err
            elif messageType == BaseTestCaseCapture.MessageType.LOG:
                assert message in self.logs.text
            else:
                pytest.fail('Unknown MessageType: ' + messageType)

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
