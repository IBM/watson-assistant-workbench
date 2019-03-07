
import os, unittest

import wawCommons

class TestAbsoluteFilePaths(unittest.TestCase):

    dataBasePath = './ci/unit_tests/wawCommons/getFilesAtPath_data/'

    def test_ifFileInDirectoryIsFound(self):
        """Tests if particular file is found by absoluteFilePaths when it's contained in supplied directory."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = list(wawCommons.absoluteFilePaths(directory))
        testFile = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile in pathList

    def test_ifFileInSubDirectoryIsFound(self):
        """Tests if file is found by absoluteFilePaths when it's contained in sub-directory of supplied directory."""
        directory = self.dataBasePath
        pathList = list(wawCommons.absoluteFilePaths(directory))
        testFile = os.path.abspath(os.path.join(directory, 'directory1', "file1.test"))
        assert testFile in pathList

    def test_ifFileInDirectoryIsNotFound(self):
        """Tests if particular file is not found by absoluteFilePaths when it's not contained in supplied directory."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        anotherDirectory = os.path.join(self.dataBasePath, 'directory2')
        pathList = list(wawCommons.absoluteFilePaths(directory))
        testFile = os.path.abspath(os.path.join(anotherDirectory, "file2.test"))
        assert testFile not in pathList

    def test_emptyPatterns(self):
        """Tests if absoluteFilePaths returns no files when no patterns supplied."""
        directory = self.dataBasePath
        pathList = list(wawCommons.absoluteFilePaths(directory, []))
        assert len(pathList) == 0

    def test_filePatternsInDirectory(self):
        """Tests if files returned from absoluteFilePaths can be filtered by patterns parameter."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = list(wawCommons.absoluteFilePaths(directory, ["*.test"]))

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 not in pathList

    def test_multiplePattterns(self):
        """Tests if mutiple patterns in absoluteFilePaths behave like there is operator OR between them."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = list(wawCommons.absoluteFilePaths(directory, ["*.test", "*"]))

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 in pathList
