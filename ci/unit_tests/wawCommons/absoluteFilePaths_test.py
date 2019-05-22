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


class TestAbsoluteFilePaths(unittest.TestCase):

    dataBasePath = './ci/unit_tests/wawCommons/getFilesAtPath_data/'

    def test_ifFileInDirectoryIsFound(self):
        """Tests if particular files are found by absoluteFilePaths when it's contained in supplied directory."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = list(wawCommons.absoluteFilePaths(directory))

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 in pathList


    def test_ifFileInSubDirectoryIsFound(self):
        """Tests if files are found by absoluteFilePaths when it's contained in sub-directory of supplied directory."""
        directory = self.dataBasePath
        pathList = list(wawCommons.absoluteFilePaths(directory))

        testFile1 = os.path.abspath(os.path.join(directory, "directory1", "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "directory1", "fileA.ext"))
        assert testFile2 in pathList


    def test_ifFileInDirectoryIsNotFound(self):
        """Tests if particular file is not found by absoluteFilePaths when it's not contained in supplied directory."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        anotherDirectory = os.path.join(self.dataBasePath, 'directory2')
        pathList = list(wawCommons.absoluteFilePaths(directory))
        testFile = os.path.abspath(os.path.join(anotherDirectory, "file2.test"))
        assert testFile not in pathList

    def test_nonExistentDirectory(self):
        """Tests if absoluteFilePaths can handle non-existent directory."""
        nonExistentDir = os.path.join(self.dataBasePath, 'non_existent_dir_123456789/')
        pathList = list(wawCommons.absoluteFilePaths(nonExistentDir))
        assert len(pathList) == 0

    def test_emptyPatterns(self):
        """Tests if absoluteFilePaths returns no files when no patterns supplied."""
        directory = self.dataBasePath
        pathList = list(wawCommons.absoluteFilePaths(directory, []))
        assert len(pathList) == 0

    def test_directoryPattern(self):
        """Tests if pattern containing directory separator does not match any file (this is intended behavior!)."""
        directory = self.dataBasePath
        pathList = list(wawCommons.absoluteFilePaths(directory, [os.path.join("directory1", "*.test")]))
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


    def test_pattternMatchMultipleFiles(self):
        """Tests if pattern in absoluteFilePaths can match multiple files."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = list(wawCommons.absoluteFilePaths(directory, ["*"]))

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 in pathList


    def test_questionMarkInPattern(self):
        """Tests if absoluteFilePaths can correctly handle question mark in pattern."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = list(wawCommons.absoluteFilePaths(directory, ["file?.*"]))

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 in pathList


    def test_rangeInPattern(self):
        """Tests if absoluteFilePaths can correctly handle question mark in pattern."""
        directory = os.path.join(self.dataBasePath, 'directory1')
        pathList = list(wawCommons.absoluteFilePaths(directory, ["file[0-9].*"]))

        testFile1 = os.path.abspath(os.path.join(directory, "file1.test"))
        assert testFile1 in pathList
        testFile2 = os.path.abspath(os.path.join(directory, "fileA.ext"))
        assert testFile2 not in pathList
