"""
Copyright 2018 IBM Corporation
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

import re
from wawCommons import eprintf
from collections import OrderedDict

class IntentData(object):
    """ Represents a single intent.    """

    def __init__(self):
        self._examples = []         # list of all text alternatives of intent

    def addExample(self, example):
        self._examples.append(example)

    def getExamples(self):
        return self._examples
