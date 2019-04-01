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

import json, sys, os, argparse, requests, configparser
from wawCommons import setLoggerConfig, getScriptLogger, getRequiredParameter, getOptionalParameter
from cfgCommons import Cfg
import logging
from deepdiff import DeepDiff

logger = getScriptLogger(__file__)

def main(argv):
    '''
    Scripts takes input json file that represents test that should be run against
    Cloud Functions and produce output that extends input json file by results
    from CFs and evaluation.

    Input json file example:
    [
        {
            "name": "test example 1", # OPTIONAL
            "type": "EXACT_MATCH", # OPTIONAL (DEFAULT = EXACT_MATCH, OPTIONS = [EXACT_MATCH])
            "cf_package": "<CLOUD FUNCTIONS PACKAGE NAME>", # OPTIONAL (could be provided directly to script, at least one has to be specified, test level overrides global script one)
            "cf_function": "<CLOUD FUNCTIONS SPECIFIC FUNCTION TO BE TESTED>", # --||--
            "input": <OBJECT> | <@PATH/TO/FILE>, # payload to be send to CF (could be specified as a relative or absolute path to the file that contains json file, e.g. "input": "@inputs/test_example_1.json")
            "outputExpected": <OBJECT> | <@PATH/TO/FILE>, # expected payload to be return from CF (--||--)
        },
        {
            "name": "test example 2",
            ...
              rest of the test definition
            ...
        }
    ]

    Output json file example:
    [
        {
            "name": "test example 1",
            ...
              rest of the input test definition
            ...
            "outputReturned": <OBJECT>, # returned payload from CF
            "result": <0 - test passed, 1 - test failed>
            "diff": <OBJECT> # if test passed then "diff" is Null, else contains object that represents differences
        }
    ]
    '''
    logger.info('STARTING: '+ os.path.basename(__file__))
    parser = argparse.ArgumentParser(description='Tests all tests specified in given file against Cloud Functions and save test outputs to output file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('inputFileName', help='File with json array containing tests.')
    parser.add_argument('outputFileName', help='File where to store test outputs.')
    # optional arguments
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('--cloudfunctions_url', required=False, help='url of cloud functions API')
    parser.add_argument('--cloudfunctions_namespace', required=False, help='cloud functions namespace')
    parser.add_argument('--cloudfunctions_package', required=False, help='cloud functions package name')
    parser.add_argument('--cloudfunctions_function', required=False, help='cloud functions specific function to be tested')
    parser.add_argument('--cloudfunctions_username', required=False, help='cloud functions user name')
    parser.add_argument('--cloudfunctions_password', required=False, help='cloud functions password')
    parser.add_argument('-v','--common_verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(argv)

    config = Cfg(args)

    VERBOSE = args.common_verbose

    url = getRequiredParameter(config, 'cloudfunctions_url')
    namespace = getRequiredParameter(config, 'cloudfunctions_namespace')
    username = getRequiredParameter(config, 'cloudfunctions_username')
    password = getRequiredParameter(config, 'cloudfunctions_password')
    package = getOptionalParameter(config, 'cloudfunctions_package')
    function = getOptionalParameter(config, 'cloudfunctions_function')

    try:
        inputFile = open(args.inputFileName, 'r')
    except IOError:
        logger.critical('Cannot open test input file %s', args.inputFileName)
        sys.exit(1)

    try:
        outputFile = open(args.outputFileName, 'w')
    except IOError:
        logger.critical('Cannot open test output file %s', args.outputFileName)
        sys.exit(1)

    try:
        inputJson = json.load(inputFile)
    except ValueError as e:
        logger.critical('Cannot decode json from test input file %s, error: %s', args.inputFileName, str(e))
        sys.exit(1)

    if not isinstance(inputJson, list):
        logger.critical('Input test json is not array!')
        sys.exit(1)

    # run tests
    testCounter = 0
    for test in inputJson:
        if not isinstance(test, dict):
            logger.error('Input test array element %d is not dictionary. Each test has to be dictionary, please see doc!', testCounter)
            continue
        logger.info('Test number: %d, name: %s', testCounter, (test['name'] if 'name' in test else '-'))
        testUrl = \
            url + ('' if url.endswith('/') else '/') + \
            namespace + '/actions/' + (test['cf_package'] if 'cf_package' in test else package) + '/' + \
            (test['cf_function'] if 'cf_function' in test else function) + \
            '?blocking=true&result=true'
        logger.info('Tested function url: %s', testUrl)

        # load test input payload json
        testInputJson = test['input']
        testInputPath = None
        try:
            if testInputJson.startswith('@'): 
                testInputPath = os.path.join(os.path.dirname(args.inputFileName), testInputJson[1:])
                logger.debug('Loading input payload from file: %s', testInputPath)
                try:
                    inputFile = open(testInputPath, 'r')
                except IOError:
                    logger.error('Cannot open input payload from file: %s', testInputPath)
                    continue
                try:
                    testInputJson = json.load(inputFile)
                except ValueError as e:
                    logger.error('Cannot decode json from input payload from file %s, error: %s', testInputPath, str(e))
                    continue
        except:
            pass

        if not testInputPath:
            logger.debug('Input payload provided inside the test')

        # load test expected output payload json
        testOutputExpectedJson = test['outputExpected']
        testOutputExpectedPath = None
        try:
            if testOutputExpectedJson.startswith('@'):
                testOutputExpectedPath = os.path.join(os.path.dirname(args.inputFileName), testOutputExpectedJson[1:])
                logger.debug('Loading expected output payload from file: %s', testOutputExpectedPath)
                try:
                    outputExpectedFile = open(testOutputExpectedPath, 'r')
                except IOError:
                    logger.error('Cannot open expected output payload from file: %s', testOutputExpectedPath)
                    continue
                try:
                    testOutputExpectedJson = json.load(outputExpectedFile)
                except ValueError as e:
                    logger.error('Cannot decode json from expected output payload from file %s, error: %s', testOutputExpectedPath, str(e))
                    continue
        except:
            pass

        if not testOutputExpectedPath:
            logger.debug('Expected output payload provided inside the test')

        # call CF
        logger.debug('Sending input json: %s', json.dumps(testInputJson, ensure_ascii=False).encode('utf8'))
        response = requests.post(
            testUrl, 
            auth=(username, password), 
            headers={'Content-Type': 'application/json'}, 
            data=json.dumps(testInputJson, ensure_ascii=False).encode('utf8'))

        responseContentType = response.headers.get('content-type')
        if responseContentType != 'application/json':
            logger.error('Response content type is not json, content type: %s, response:\n%s', responseContentType, response.text)
            continue

        # check status
        if response.status_code == 200:
            testOutputReturnedJson = response.json()
            logger.debug('Received output json: %s', json.dumps(testOutputReturnedJson, ensure_ascii=False).encode('utf8'))
            test['outputReturned'] = testOutputReturnedJson

            # evaluate test
            if 'type' not in test or test['type'] == 'EXACT_MATCH':
                testResultString = DeepDiff(testOutputExpectedJson, testOutputReturnedJson, ignore_order=True).json
                testResultJson = json.loads(testResultString)
                if testResultJson == {}:
                    test['result'] = 0
                else:
                    test['result'] = 1
                    test['diff'] = testResultJson
            else:
                logger.error('Unknown test type: %s', test['type'])
        elif response.status_code in [202, 403, 404, 408]:
            # 202 Accepted activation request (should not happen while sending 'blocking=true&result=true')
            # 403 Forbidden (could be just for specific package or function)
            # 404 Not Found (action or package could be incorrectly specified for given test)
            # 408 Request Timeout (could happen e.g. for CF that calls some REST APIs, e.g. Discovery service)
            # 502 Bad Gateway (when the CF raises exception, e.g. bad params where provided)
            # => Could be issue just for given test, so we don't want to stop whole testing.
            logger.error('Unexpected response status: %d, response: %s', response.status_code, json.dumps(response.json(), ensure_ascii=False).encode('utf8'))
        else:
            # 401 Unauthorized (while we use same credentials for all tests then we want to end after the first test returns bad authentification)
            # 500 Internal Server Error (could happen that IBM Cloud has several issue and is not able to handle incoming requests, then it would be probably same for all tests)
            # => We don't want to continue with testing.
            logger.critical('Unexpected response status (cannot continue with testing): %d, response: %s', response.status_code, json.dumps(response.json(), ensure_ascii=False).encode('utf8'))
            sys.exit(1)

        testCounter += 1

    outputFile.write(json.dumps(inputJson, indent=4, ensure_ascii=False).encode('utf8') + '\n')
    logger.info('FINISHING: '+ os.path.basename(__file__))

if __name__ == '__main__':
    setLoggerConfig()
    main(sys.argv[1:])

