
import os, unittest

import wawCommons

class TestGetFilesAtPath(unittest.TestCase):

    dataBasePath = './ci/unit_tests/wawCommons/getFilesAtPath_data/'

    def test_emptyInputList(self):
        """Tests if getFilesAtPath function works when pathList parameter is empty."""
        pathList = wawCommons.getFilesAtPath([])
        assert len(pathList) == 0

    def test_ifFileInDirectoryIsFound(self):
        """Tests if particular file is found by getFilesAtPath when it's contained in supplied directory."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = wawCommons.getFilesAtPath([directory])
        testFile = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile in pathList

    def test_ifFileInSubDirectoryIsFound(self):
        """Tests if file is found by getFilesAtPath when it's contained in sub-directory of supplied directory."""
        directory = self.dataBasePath
        pathList = wawCommons.getFilesAtPath([directory])
        testFile = os.path.abspath(os.path.join(directory, 'directory1', "file1.test"))
        assert testFile in pathList

    def test_ifFileInDirectoryIsNotFound(self):
        """Tests if particular file is not found by getFilesAtPath when it's not contained in supplied directory."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        anotherDirectory = os.path.join(self.dataBasePath, 'directory2')
        pathList = wawCommons.getFilesAtPath([directory])
        testFile = os.path.abspath(os.path.join(anotherDirectory, "file2.test"))
        assert testFile not in pathList

    def test_ifFileInOneDirectoryIsFound(self):
        """Tests if particular file is found by getFilesAtPath when it's contained in one of supplied directories."""
        directory1 = os.path.join(self.dataBasePath, 'directory1')
        directory2 = os.path.join(self.dataBasePath, 'directory2')
        pathList = wawCommons.getFilesAtPath([directory1, directory2])

        testFile1 = os.path.abspath(os.path.join(directory1, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory2, "file2.test"))
        assert testFile2 in pathList


    def test_nonExistentFile(self):
        """Tests if getFilesAtPath ignores non-existent file."""
        nonExistentFile = os.path.join(self.dataBasePath, 'non_existing_file_123456789.test')
        pathList = wawCommons.getFilesAtPath([nonExistentFile])
        assert len(pathList) == 0

    def test_ifFilePathIsFound(self):
        """Tests if getFilesAtPath returns file when it is directly supplied in input list."""
        filePath = os.path.join(self.dataBasePath, 'directory1', 'file1.test')
        pathList = wawCommons.getFilesAtPath([filePath])
        absPath = os.path.abspath(filePath)
        assert len(pathList) == 1
        assert absPath in pathList

    def test_ifFilePathsIsFound(self):
        """Tests if getFilesAtPath returns files when they are directly supplied in input list."""
        filePath1 = os.path.join(self.dataBasePath, 'directory1', 'file1.test')
        filePath2 = os.path.join(self.dataBasePath, 'directory2', 'file2.test')
        pathList = wawCommons.getFilesAtPath([filePath1, filePath2])

        assert len(pathList) == 2
        absPath1 = os.path.abspath(filePath1)
        assert absPath1 in pathList
        absPath2 = os.path.abspath(filePath2)
        assert absPath2 in pathList


    def test_filePathAndDirectoryCombination(self):
        """Tests if getFilesAtPath when there is a combination of file and directory in input parameter."""
        filePath = os.path.join(self.dataBasePath, 'directory1', 'file1.test')
        directory = os.path.join(self.dataBasePath, 'directory2')
        pathList = wawCommons.getFilesAtPath([filePath, directory])

        testFile1 = os.path.abspath(filePath)
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "file2.test"))
        assert testFile2 in pathList


    def test_emptyPatterns(self):
        """Tests if getFilesAtPath returns no files when no patterns supplied."""
        directory = self.dataBasePath
        pathList = wawCommons.getFilesAtPath([directory], [])
        assert len(pathList) == 0

    def test_filePatternsInDirectory(self):
        """Tests if files returned from getFilesAtPath can be filtered by patterns parameter."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = wawCommons.getFilesAtPath([directory], ["*.test"])

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 not in pathList


    def test_filePatternsOnFilePath(self):
        """Tests if file returned from getFilesAtPath can be filtered by patterns parameter."""
        filePath1 = os.path.join(self.dataBasePath, 'directory1', 'file1.test')
        filePath2 = os.path.join(self.dataBasePath, 'directory1', 'fileA.ext')
        pathList = wawCommons.getFilesAtPath([filePath1, filePath2], ["*.test"])

        assert len(pathList) == 1
        absPath1 = os.path.abspath(filePath1)
        assert absPath1 in pathList
        absPath2 = os.path.abspath(filePath2)
        assert absPath2 not in pathList


    def test_multiplePattterns(self):
        """Tests if mutiple patterns in getFilesAtPath behave like there is operator OR between them."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = wawCommons.getFilesAtPath([directory], ["*.test", "*"])

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 in pathList
