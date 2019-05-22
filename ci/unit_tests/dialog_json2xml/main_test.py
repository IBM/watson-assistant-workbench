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

from lxml import etree

import dialog_json2xml

from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    testOutputPath = os.path.join(dataBasePath, 'outputs')


    def setup_class(cls):
        ''' Setup any state specific to the execution of the given class (which usually contains tests). '''
        # create output folder
        BaseTestCaseCapture.createFolder(TestMain.testOutputPath)

    def callfunc(self, *args, **kwargs):
        dialog_json2xml.main(*args, **kwargs)

    def test_mainValidActions(self):
        """Tests if the script successfully completes with valid input file with actions."""
        inputJsonPath = os.path.abspath(os.path.join(self.dataBasePath, 'inputActionsValid.json'))
        expectedXmlPath = os.path.abspath(os.path.join(self.dataBasePath, 'expectedActionsValid.xml'))

        outputXmlDirPath = os.path.join(self.testOutputPath, 'outputActionsValidResult')
        outputXmlPath = os.path.join(outputXmlDirPath, 'dialog.xml')

        BaseTestCaseCapture.createFolder(outputXmlDirPath)

        self.t_noException([[inputJsonPath, '-d', outputXmlDirPath]])

        with open(expectedXmlPath, 'r') as expectedXmlFile:
            expectedXml = etree.XML(expectedXmlFile.read(), etree.XMLParser(remove_blank_text=True))
            for parent in expectedXml.xpath('//*[./*]'): # Search for parent elements
                parent[:] = sorted(parent, key=lambda x: x.tag)
        with open(outputXmlPath, 'r') as outputXmlFile:
            outputXml = etree.XML(outputXmlFile.read(), etree.XMLParser(remove_blank_text=True))
            for parent in outputXml.xpath('//*[./*]'): # Search for parent elements
                parent[:] = sorted(parent, key=lambda x: x.tag)

        assert etree.tostring(expectedXml) == etree.tostring(outputXml)
