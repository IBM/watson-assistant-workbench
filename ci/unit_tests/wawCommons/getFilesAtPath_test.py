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
import unittest

import wawCommons


class TestGetFilesAtPath(unittest.TestCase):

    dataBasePath = './ci/unit_tests/wawCommons/getFilesAtPath_data/'

    def test_emptyInputList(self):
        """Tests if getFilesAtPath function works when pathList parameter is empty."""
        pathList = wawCommons.getFilesAtPath([])
        assert len(pathList) == 0

    def test_ifFileInDirectoryIsFound(self):
        """Tests if particular files are found by getFilesAtPath when it's contained in supplied directory."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = wawCommons.getFilesAtPath([directory])

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 in pathList


    def test_ifFileInSubDirectoryIsFound(self):
        """Tests if files are found by getFilesAtPath when it's contained in sub-directory of supplied directory."""
        directory = self.dataBasePath
        pathList = wawCommons.getFilesAtPath([directory])

        testFile1 = os.path.abspath(os.path.join(directory, "directory1", "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "directory1", "fileA.ext"))
        assert testFile2 in pathList


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


    def test_nonExistentDirectory(self):
        """Tests if getFilesAtPath can handle non-existent directory."""
        nonExistentDir = os.path.join(self.dataBasePath, 'non_existent_dir_123456789/')
        pathList = wawCommons.getFilesAtPath([nonExistentDir])
        assert len(pathList) == 0

    def test_nonExistentAndExistentDirectory(self):
        """Tests if getFilesAtPath ignores non-existent directory in list."""
        nonExistentDir = os.path.join(self.dataBasePath, 'non_existent_dir_123456789/')
        existentDir = os.path.join(self.dataBasePath, 'directory1')

        pathList = wawCommons.getFilesAtPath([nonExistentDir, existentDir])
        testFile1 = os.path.abspath(os.path.join(existentDir, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(existentDir, "fileA.ext"))
        assert testFile2 in pathList


    def test_nonExistentFile(self):
        """Tests if getFilesAtPath ignores non-existent file."""
        nonExistentFile = os.path.join(self.dataBasePath, 'non_existent_file_123456789.test')
        pathList = wawCommons.getFilesAtPath([nonExistentFile])
        assert len(pathList) == 0

    def test_nonExistentAndExistentFile(self):
        """Tests if getFilesAtPath ignores non-existent files in list."""
        nonExistentFile = os.path.join(self.dataBasePath, 'non_existent_file_123456789.test')
        existentFile = os.path.join(self.dataBasePath, 'directory1', 'file1.test')
        pathList = wawCommons.getFilesAtPath([nonExistentFile, existentFile])
        absPath = os.path.abspath(existentFile)
        assert len(pathList) == 1
        assert absPath in pathList

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

    def test_directoryPattern(self):
        """Tests if pattern containing directory separator does not match any file (this is intended behavior!)."""
        directory = self.dataBasePath
        pathList = wawCommons.getFilesAtPath([directory], [os.path.join("directory1", "*.test")])
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


    def test_multiplePattternsOnMultipleDirectories(self):
        """Tests if getFilesAtPath can handle multiple patterns combined with mutiple input directories."""
        directory1 = os.path.join(self.dataBasePath, 'directory1')
        directory2 = os.path.join(self.dataBasePath, 'directory2')
        pathList = wawCommons.getFilesAtPath([directory1, directory2], ["*.test", "*"])

        testFile1 = os.path.abspath(os.path.join(directory1, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory1, "fileA.ext"))
        assert testFile2 in pathList
        testFile3 = os.path.abspath(os.path.join(directory2, "file2.test"))
        assert testFile3 in pathList


    def test_multiplePattternsOnFileDirectoryCombination(self):
        """Tests if getFilesAtPath can handle multiple patterns combined with input directory and separated file."""
        filePath = os.path.join(self.dataBasePath, 'directory1', 'file1.test')
        directory = os.path.join(self.dataBasePath, 'directory2')
        pathList = wawCommons.getFilesAtPath([filePath, directory], ["*.test", "*"])

        testFile1 = os.path.abspath(filePath)
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(self.dataBasePath, 'directory1', "fileA.ext"))
        assert testFile2 not in pathList
        testFile3 = os.path.abspath(os.path.join(directory, "file2.test"))
        assert testFile3 in pathList


    def test_pattternMatchMultipleFiles(self):
        """Tests if pattern in getFilesAtPath can match multiple files."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = wawCommons.getFilesAtPath([directory], ["*"])

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 in pathList


    def test_questionMarkInPattern(self):
        """Tests if getFilesAtPath can correctly handle question mark in pattern."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = wawCommons.getFilesAtPath([directory], ["file?.*"])

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 in pathList


    def test_rangeInPattern(self):
        """Tests if getFilesAtPath can correctly handle question mark in pattern."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = wawCommons.getFilesAtPath([directory], ["file[0-9].*"])

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 not in pathList
