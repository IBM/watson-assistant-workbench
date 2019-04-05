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

import pytest, unittest

import wawCommons
from ...test_utils import BaseTestCaseCapture

class TestConvertApikeyToUsernameAndPassword(BaseTestCaseCapture):

    def callfunc(self, *args, **kwargs):
        wawCommons.convertApikeyToUsernameAndPassword(*args, **kwargs)

    def test_none(self):
        ''' Tests if apikey is None '''
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL Apikey has invalid format (valid format is string: \'username:password\')', 
            [None]
        )

    def test_onePartAfterSplit(self):
        ''' Tests if apikey is does not contains \':\' '''
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL Apikey has invalid format (valid format is string: \'username:password\')', 
            ['aaa']
        )

    def test_toManyPartsAfterSplit(self):
        ''' Tests if apikey is has to many \':\' '''
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL Apikey has invalid format (valid format is string: \'username:password\')', 
            ['aaa:bbb:ccc']
        )

    def test_validApikey(self):
        ''' Tests if valid apikey is split correctly '''
        username, password = wawCommons.convertApikeyToUsernameAndPassword('aaa:bbb')
        assert username == 'aaa'
        assert password == 'bbb'

