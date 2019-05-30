'''
Copyright 2018 IBM Corporation
Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import argparse
import datetime
import json
import logging
import os
import sys

from deepdiff import DeepDiff
from junitparser import Error, Failure, JUnitXml, TestCase, TestSuite

from cfgCommons import Cfg
from wawCommons import getScriptLogger, setLoggerConfig, getOptionalParameter

logger = getScriptLogger(__file__)

def main(argv):
    parser = argparse.ArgumentParser(description='Evaluates all test output against Cloud Functions specified in given file and save evaluation output to output file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('inputFileName', help='File with json array containing test output.')
    parser.add_argument('outputFileName', help='File where to store evaluation output.')
    # optional arguments
    parser.add_argument('-j', '--junitFileName', required=False, help='File where to store evaluation JUnit XML output (if not specified, no JUnit XML output is generated).')
    parser.add_argument('--className', required=False, help="Default value for test class name (it is overwritten by 'class' values inside given test output as an input).")
    parser.add_argument('--suitName', required=False, help="Default value for test suit name (if not provided the name of the file is taken).")
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    config = Cfg(args)

    logger.info('STARTING: '+ os.path.basename(__file__))

    try:
        inputFile = open(args.inputFileName, 'r')
    except IOError:
        logger.critical("Cannot open test output file '%s'", args.inputFileName)
        sys.exit(1)

    try:
        outputFile = open(args.outputFileName, 'w')
    except IOError:
        logger.critical("Cannot open evaluation output file '%s'", args.outputFileName)
        sys.exit(1)

    junitFileName = getOptionalParameter(config, 'junitFileName')
    if junitFileName:
        try:
            # we just want to check that file is writeable before passing to junitxml writer
            open(junitFileName, 'w')
        except IOError:
            logger.critical("Cannot open evaluation JUnit XML output file '%s'", junitFileName)
            sys.exit(1)

    try:
        inputJson = json.load(inputFile)
    except ValueError as e:
        logger.critical("Cannot decode json from test output file '%s', error '%s'", args.inputFileName, str(e))
        sys.exit(1)

    if not isinstance(inputJson, list):
        logger.critical("Test output json is not array!")
        sys.exit(1)

    # run evaluation
    xml = JUnitXml()
    suitName = getOptionalParameter(config, 'suitName') or os.path.basename(args.inputFileName).split('.')[0]
    suitName = suitName.replace(' ', '_')
    classNameDefault = getOptionalParameter(config, 'className')
    suite = TestSuite(suitName) # once we support multiple test files then for each one should be test suite created
    xml.add_testsuite(suite)
    suite.timestamp = str(datetime.datetime.now()) # time of evaluation, not the testing it self (evaluations could differ)
    #suite.hostname = '<Host on which the tests were executed. 'localhost' should be used if the hostname cannot be determined.>'
    testCounter = -1
    for test in inputJson:
        testCounter += 1
        case = TestCase()
        suite.add_testcase(case)

        if classNameDefault:
            case.classname = suitName + '.' + classNameDefault.replace(' ', '_')

        if not isinstance(test, dict):
            errorMessage = "Test output array element {:d} is not dictionary. Each test output has to be dictionary, please see doc!".format(testCounter)
            logger.error(errorMessage)
            case.result = Error(errorMessage, 'ValueError')
            continue

        logger.info("Test number %d, name '%s'", testCounter, test.get('name', '-'))
        case.name = test.get('name', None)

        if 'class' in test:
            case.classname = suitName + '.' + test.get('class').replace(' ', '_')

        if 'time' in test:
            time = test.get('time')
            if isinstance(time, int):
                case.time = test.get('time')
            else:
                logger.warning("Time is not type of integer, type '%s'", str(type(time).__name__))

        # propagate error from test script
        if 'error' in test:
            message = test['error']['message'] if 'message' in test['error'] else ''
            error = test['error']['type'] if 'type' in test['error'] else ''
            logger.error("Test output contains error, error type '{}' and message '{}'".format(message, error))
            case.result = Error(message, error)
            continue

        # load test expected output payload json
        testOutputExpectedJson = test['outputExpected']
        testOutputExpectedPath = None
        try:
            if testOutputExpectedJson.startswith('@'):
                testOutputExpectedPath = os.path.join(os.path.dirname(args.inputFileName), testOutputExpectedJson[1:])
                logger.debug("Loading expected output payload from file '%s'", testOutputExpectedPath)
                try:
                    outputExpectedFile = open(testOutputExpectedPath, 'r')
                except IOError:
                    errorMessage = "Cannot open expected output payload from file '{}'".format(testOutputExpectedPath)
                    logger.error(errorMessage)
                    case.result = Error(errorMessage, 'IOError')
                    continue
                try:
                    testOutputExpectedJson = json.load(outputExpectedFile)
                except ValueError as e:
                    errorMessage = "Cannot decode json from expected output payload from file '{}', error '{}'".format(testOutputExpectedPath, str(e))
                    logger.error(errorMessage)
                    case.result = Error(errorMessage, 'ValueError')
                    continue
        except AttributeError:
            pass

        if not testOutputExpectedPath:
            logger.debug("Expected output payload provided inside the test")

        # load test returned output payload json
        testOutputReturnedJson = test['outputReturned']
        testOutputReturnedPath = None
        try:
            if testOutputReturnedJson.startswith('@'):
                testOutputReturnedPath = os.path.join(os.path.dirname(args.inputFileName), testOutputReturnedJson[1:])
                logger.debug("Loading returned output payload from file '%s'", testOutputReturnedPath)
                try:
                    outputReturnedFile = open(testOutputReturnedPath, 'r')
                except IOError:
                    errorMessage = "Cannot open returned output payload from file '{}'".format(testOutputReturnedPath)
                    logger.error(errorMessage)
                    case.result = Error(errorMessage, 'IOError')
                    continue
                try:
                    testOutputReturnedJson = json.load(outputReturnedFile)
                except ValueError as e:
                    errorMessage = "Cannot decode json from returned output payload from file '{}', error '{}'".format(testOutputReturnedPath, str(e))
                    logger.error(errorMessage)
                    case.result = Error(errorMessage, 'ValueError')
                    continue
        except AttributeError:
            pass

        if not testOutputReturnedPath:
            logger.debug("Returned output payload provided inside the test")

        # evaluate test
        if 'type' not in test or test['type'] == 'EXACT_MATCH':
            testResultString = DeepDiff(testOutputExpectedJson, testOutputReturnedJson, ignore_order=True).json
            testResultJson = json.loads(testResultString)
            if testResultJson == {}:
                test['result'] = 0
            else:
                test['result'] = 1
                test['diff'] = testResultJson
                case.result = Failure(json.dumps(testResultJson, sort_keys=True))
        else:
            errorMessage = "Unknown test type: {}".format(test['type'])
            logger.error(errorMessage)
            case.result = Error(errorMessage, 'ValueError')

    # write outputs
    if junitFileName:
        xml.update_statistics()
        xml.write(junitFileName, True)
    outputFile.write(json.dumps(inputJson, indent=4, ensure_ascii=False) + '\n')

    logger.info('FINISHING: '+ os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])
