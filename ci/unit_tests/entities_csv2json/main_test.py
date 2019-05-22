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

import entities_csv2json
import os, json
from deepdiff import DeepDiff
from ...test_utils import BaseTestCaseCapture

class TestMain(BaseTestCaseCapture):
    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')

    def callfunc(self, *args, **kwargs):
        entities_csv2json.main(*args, **kwargs)

    def test_globalFuzzy(self):
        ''' Test for setting of global fuzzy entity matching'''
        dataPath = os.path.join(self.dataBasePath, "fuzzyMatching")
        inputPath = os.path.join(dataPath, "input")
        outputsPath = os.path.join(self.dataBasePath, 'outputs')

        for files in [("fuzzyOn.cfg", "fuzzyOn.json", "fuzzyOnExpected.json"),
                    ("fuzzyOff.cfg", "fuzzyOff.json", "fuzzyOffExpected.json"),
                    ("fuzzyOffEmpty.cfg", "fuzzyOff.json", "fuzzyOffExpected.json")]:
            cfgPath = os.path.join(self.dataBasePath, files[0])
            outputJsonFileName = files[1]
            expectedJsonPath = os.path.join(dataPath, files[2])
            params = ["-c", cfgPath,
                    "-ie", inputPath,
                    "-od", outputsPath,
                    "-oe", outputJsonFileName]
            outputJsonPath = os.path.join(outputsPath, outputJsonFileName)
            self.t_noException([params])
            with open(expectedJsonPath, 'r') as expectedJsonFile, open(outputJsonPath, 'r') as outputJsonFile:
                result = DeepDiff(json.load(expectedJsonFile), json.load(outputJsonFile), ignore_order=True).json
                assert result == '{}'
