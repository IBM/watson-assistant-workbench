
import os, pytest, unittest

class TestCaseCapture(unittest.TestCase):

    ''' Runs function with given arguments and tests if it fails and error message contains \'too few arguments\' '''
    def tTooFewArgs(self, *args, **kwargs):
        self.tExitCodeAndErrMessage(2, 'too few arguments', *args, **kwargs)

    ''' Runs function with given arguments and tests if it fails and error message contains \'unrecognized arguments\' '''
    def tUnrecognizedArgs(self, *args, **kwargs):
        self.tExitCodeAndErrMessage(2, 'unrecognized arguments', *args, **kwargs)

    ''' Runs function with given arguments and tests exit code '''
    def tExitCode(self, exitCode, *args, **kwargs):
        self.tExitCodeAndErrMessage(exitCode, '', *args, **kwargs)

    ''' (Generic) Runs function with given arguments and tests exit code and error message '''
    def tExitCodeAndErrMessage(self, exitCode, errMessage, *args, **kwargs):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            self.callfunc(*args, **kwargs)
        captured = self.capfd.readouterr()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == exitCode
        assert errMessage in captured.err

    ''' (Generic) Runs function with given arguments and tests exception '''
    def tRaiseError(self, errorType, errMessage, *args, **kwargs):
        with pytest.raises(errorType) as pytest_wrapped_e:
            self.callfunc(*args, **kwargs)
        captured = self.capfd.readouterr()
        assert pytest_wrapped_e.type == errorType
        assert errMessage in pytest_wrapped_e.value

    ''' (Need to be overidden) Function to be called and tested '''
    def callfunc(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

