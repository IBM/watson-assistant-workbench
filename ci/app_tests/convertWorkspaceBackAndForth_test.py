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

import os, pytest

import compare_dialogs
import dialog_json2xml
import dialog_xml2json
from ..test_utils import BaseTestCaseCapture

class TestConvertWorkspaceBackAndForth(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'convertWorkspaceBackAndForth_data' + os.sep)
    testOutputPath = os.path.join(dataBasePath, 'outputs')

    def setup_class(cls):
        ''' Setup any state specific to the execution of the given class (which usually contains tests). '''
        BaseTestCaseCapture.createFolder(TestConvertWorkspaceBackAndForth.testOutputPath)

    @pytest.mark.parametrize('dialogFilename', ['dialog_1.json', 'dialog_2.json', 'dialog_3.json'])
    def test_basic(self, dialogFilename):
        ''' Tests if json converted to xml and back is same as source. '''
        # prepare paths
        configPath = os.path.abspath(os.path.join(self.dataBasePath, 'build.cfg'))
        dialogJsonRefPath = os.path.abspath(os.path.join(self.dataBasePath, dialogFilename))
        dialogJsonHypPath = os.path.abspath(os.path.join(self.testOutputPath, dialogFilename))
        dialogXmlPath = os.path.abspath(os.path.join(self.testOutputPath, os.path.splitext(dialogFilename)[0] + '.xml'))

        # convert json to xml (we need to take captured.out because xml is printed to output)
        self.t_fun_noException(dialog_json2xml.main, [[dialogJsonRefPath]])
        with open(dialogXmlPath, 'w') as f:
            f.write(self.captured.out)

        # convert xml back to json
        self.t_fun_noException(dialog_xml2json.main, [['-dm', dialogXmlPath, '-of', self.testOutputPath, '-od', dialogFilename, '-c', configPath, '-v']])

        # compare dialogs if they are same
        self.t_fun_exitCode(compare_dialogs.main, 0, [[dialogJsonRefPath, dialogJsonHypPath]])

