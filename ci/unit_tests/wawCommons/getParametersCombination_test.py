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

import argparse

import wawCommons

from cfgCommons import Cfg
from ...test_utils import BaseTestCaseCapture

class TestGetParametersCombination(BaseTestCaseCapture):

    def callfunc(self, *args, **kwargs):
        wawCommons.getParametersCombination(*args, **kwargs)

    def test_configNull(self):
        ''' Tests if configuration file is Null '''

        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL config is null', 
            [None, 'parameter']
        )

    def test_noParametersCombination(self):
        ''' Tests if no parameters combination is provided '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        config = Cfg(args)
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL no parameters combination provided to be retrieved', 
            [config]
        )

    def test_badParametersCombinationType(self):
        ''' Tests if type of parameters combination is provided '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        config = Cfg(args)
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL arguments could be only parameter names or array of parameters names, arg type \'dict\'', 
            [config, {}]
        )

    def test_missingParametersCombinationString(self):
        ''' Tests if one combination (one parameter provided as string) is missing in config '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        config = Cfg(args)
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL Combination 0: \'parameterName\'', 
            [config, 'parameterName']
        )

    def test_missingParametersCombinationList(self):
        ''' Tests if one combination (two parameters provided as list) is missing in config '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        config = Cfg(args)
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL Combination 0: \'[\'parameterNameA\', \'parameterNameB\']\'', 
            [config, ['parameterNameA', 'parameterNameB']]
        )

    def test_missingParametersCombinationMix(self):
        ''' Tests if two combinations (one parameter provided as string and two parameters provided as list) are missing in config '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        config = Cfg(args)
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL Combination 1: \'parameterNameC\'', 
            [config, ['parameterNameA', 'parameterNameB'], 'parameterNameC']
        )

    def test_missingParametersCombinationListPart(self):
        ''' Tests if one combination (two parameters provided as list) is missing in config but one parameter is set '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        args.parameterNameA = 'parameterNameAValue'
        config = Cfg(args)
        self.t_exitCodeAndLogMessage(
            1, 
            'missing parameters: \'[\'parameterNameB\']\'', 
            [config, ['parameterNameA', 'parameterNameB']]
        )

    def test_moreParametersCombinationProvidedAB(self):
        ''' Tests if two combinations (one parameter provided as string and two parameters provided as list) are provided in config, variant AB '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        args.parameterNameA = 'parameterNameAValue'
        args.parameterNameB = 'parameterNameBValue'
        args.parameterNameC = 'parameterNameCValue'
        config = Cfg(args)
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL only one combination of parameters can be set, combination already set: \'[\'parameterNameA\', \'parameterNameB\']\', another argument set: \'parameterNameC\'', 
            [config, ['parameterNameA', 'parameterNameB'], 'parameterNameC']
        )

    def test_moreParametersCombinationProvidedC(self):
        ''' Tests if two combinations (one parameter provided as string and two parameters provided as list) are provided in config, variant C '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        args.parameterNameA = 'parameterNameAValue'
        args.parameterNameB = 'parameterNameBValue'
        args.parameterNameC = 'parameterNameCValue'
        config = Cfg(args)
        self.t_exitCodeAndLogMessage(
            1, 
            'CRITICAL only one combination of parameters can be set, combination already set: \'[\'parameterNameC\']\', another argument set: \'parameterNameA\'', 
            [config, 'parameterNameC', ['parameterNameA', 'parameterNameB']]
        )

    def test_parametersCombinationString(self):
        ''' Tests if one combination (one parameter provided as string) is returned from config '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        args.parameterName = 'parameterNameValue'
        config = Cfg(args)
        rc = wawCommons.getParametersCombination(config, 'parameterName')
        assert rc == {
            'parameterName': 'parameterNameValue'
        }

    def test_parametersCombinationList(self):
        ''' Tests if one combination (two parameters provided as list) is returned from config '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        args.parameterNameA = 'parameterNameAValue'
        args.parameterNameB = 'parameterNameBValue'
        config = Cfg(args)
        rc = wawCommons.getParametersCombination(config, ['parameterNameA', 'parameterNameB'])
        assert rc == {
            'parameterNameA': 'parameterNameAValue',
            'parameterNameB': 'parameterNameBValue',
        }

    def test_parametersCombinationMixAB(self):
        ''' Tests if one combination (one parameter provided as string and two parameters provided as list) is returned from config, variant AB '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        args.parameterNameA = 'parameterNameAValue'
        args.parameterNameB = 'parameterNameBValue'
        config = Cfg(args)
        rc = wawCommons.getParametersCombination(config, 'parameterNameC', ['parameterNameA', 'parameterNameB'])
        assert rc == {
            'parameterNameA': 'parameterNameAValue',
            'parameterNameB': 'parameterNameBValue',
        }

    def test_parametersCombinationMixC(self):
        ''' Tests if one combination (one parameter provided as string and two parameters provided as list) is returned from config, variant C '''
        args = argparse.Namespace()
        args.common_configFilePaths = None
        args.parameterNameC = 'parameterNameCValue'
        config = Cfg(args)
        rc = wawCommons.getParametersCombination(config, 'parameterNameC', ['parameterNameA', 'parameterNameB'])
        assert rc == {
            'parameterNameC': 'parameterNameCValue'
        }

