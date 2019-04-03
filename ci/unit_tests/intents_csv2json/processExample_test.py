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

import intents_csv2json
from ...test_utils import BaseTestCaseCapture

class TestProcessExample(BaseTestCaseCapture):

    def callfunc(self, *args, **kwargs):
        intents_csv2json.processExample(*args, **kwargs)

    def test_intentWithoutEntity(self):
        ''' Test for basic intent'''
        expectedResult =  { "text": "hello world example" }
        result = intents_csv2json.processExample('hello world example', 'TestIntent', [])
        assert result == expectedResult

    def test_intentWithOneEntity(self):
        ''' Test for one contextual entity in intent'''
        expectedResult = {
                "text": "this is green color",
                "mentions": [
                    {
                        "location": [
                            8,
                            13
                        ],
                        "entity": "color"
                    }
                ]
            }
        result = intents_csv2json.processExample('this is <color>green</color> color', 'TestIntent', [])
        assert result == expectedResult

    def test_intentWithMoreEntities(self):
        ''' Test for one contextual entity in intent'''
        expectedResult = {
                "text": "roses are red",
                "mentions": [
                    {
                        "location": [
                            0,
                            5
                        ],
                        "entity": "flower"
                    },
                    {
                        "location": [
                            10,
                            13
                        ],
                        "entity": "color"
                    }
                ]
            }
        result = intents_csv2json.processExample('<flower>roses</flower> are <color>red</color>', 'TestIntent', [])
        assert result == expectedResult

    def test_intentWithNestedEntities(self):
        ''' Test for nested entities'''
        expectedResult = {
                "text": "very tall green tree",
                "mentions": [
                    {
                        "location": [
                            10,
                            15
                        ],
                        "entity": "color"
                    }
                ]
            }
        result = intents_csv2json.processExample('<plant>very tall <color>green</color> tree</plant>', 'TestIntent', [])
        assert result == expectedResult
        assert 'omitting outer tag annotation: <plant>' in self.caplog.text

    def test_intentWithMoreNestedEntities(self):
        ''' Test for nested entities'''
        expectedResult = {
                "text": "small brown pine",
                "mentions": [
                    {
                        "location": [
                            0,
                            5
                        ],
                        "entity": "size"
                    },
                    {
                        "location": [
                            6,
                            11
                        ],
                        "entity": "color"
                    }
                ]
            }
        result = intents_csv2json.processExample('<plant><size>small</size> <color>brown</color> pine</plant>', 'TestIntent', [])
        assert result == expectedResult
        assert 'omitting outer tag annotation: <plant>' in self.caplog.text

    def test_intentWithManyLevelNestedEntities(self):
        ''' Test for nested entities'''
        expectedResult = {
                "text": "hello world, how are you? this is black",
                "mentions": [
                    {
                        "location": [
                            34,
                            39
                        ],
                        "entity": "color"
                    }
                ]
            }
        result = intents_csv2json.processExample('<level2>hello <level1>world, how are you? this is <color>black</color></level1></level2>', 'TestIntent', [])
        assert result == expectedResult
        assert 'omitting outer tag annotation: <level2>' in self.caplog.text
        assert 'omitting outer tag annotation: <level1>' in self.caplog.text

    def test_intentAlreadyExisting(self):
        ''' Test for nested entities'''
        expectedResult = None
        result = intents_csv2json.processExample('<hey>nothing <test>like</test> the above</hey>', 'TestIntent', [{"text": "nothing like the above"}])
        assert result == expectedResult
        assert 'Example used twice for the intent TestIntent, omitting: nothing like the above' in self.caplog.text

    def test_intentAnnontationButEmpty(self):
        ''' Test for nested entities'''
        expectedResult = None
        result = intents_csv2json.processExample('<empty></empty>', 'TestIntent', [])
        assert result == expectedResult
        assert 'Omitting empty line for intent TestIntent after annotation tags are removed: <empty></empty>' in self.caplog.text

    def test_intentInvalidAnnotation(self):
        ''' Test for nested entities'''
        self.t_exitCodeAndLogMessage(1, 'Invalid annotation tag for the intent TestIntent, </in>', ['#Doing $some <tags> @ which ~ are <not> </in> </not> correct @what?', 'TestIntent', []])
