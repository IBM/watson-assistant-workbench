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

import pytest

from ..test_utils import BaseTestCaseCapture

class TestSkipiffails(BaseTestCaseCapture):

    def test_withoutMarkLabel(self):
        ''' Tests if not providing 'skipiffails' mark does not brake anything (implementation in ci/confest.py).'''
        assert 1

    @pytest.mark.skipiffails()
    def test_withoutLabel(self):
        ''' Tests if the 'skipiffails' mark does not brake anything (implementation in ci/confest.py).
        Test should be skipped and assertion should be printed to warnings.'''
        assert 0

    @pytest.mark.skipiffails(label='A label')
    def test_withLabel(self):
        ''' Tests if the 'skipiffails' mark does not brake anything (implementation in ci/confest.py).
        Test should be skipped and assertion along with label should be printed to warnings.'''
        assert 0
