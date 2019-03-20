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

import os, json, sys, argparse, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from cfgCommons import Cfg
from wawCommons import setLoggerConfig, getScriptLogger, getFilesAtPath
import urllib3
import logging


logger = getScriptLogger(__file__)


if __name__ == '__main__':
    setLoggerConfig()
    logger.info('STARTING: '+ os.path.basename(__file__))
    parser = argparse.ArgumentParser(description='Concatenate intents, entities and dialogue jsons to Watson Conversation Service workspace .json format', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-offnc', '--functions', required=False, help='directory where the cloud functions are located')
    parser.add_argument('-cfspc', '--cloudfunctions_namespace', required=False, help='cloud functions namespace')
    parser.add_argument('-cfname', '--cloudfunctions_username', required=False, help='cloud functions user name')
    parser.add_argument('-cfpswd', '--cloudfunctions_password', required=False, help='cloud functions password')
    parser.add_argument('-cfpack', '--cloudfunctions_package', required=False, help='package name')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    config = Cfg(args)
    VERBOSE = args.verbose

    intentsJSON = {}
    if not hasattr(config, 'cloudfunctions_namespace'):
        logger.error('cloudfunctions_namespace  not specified.')
        exit(1)
    if not hasattr(config, 'cloudfunctions_password'):
        logger.error('cloudfunctions_password  not specified.')
        exit(1)
    if not hasattr(config, 'cloudfunctions_package'):
        logger.error('cloudfunctions_package  not specified.')
        exit(1)

    if not hasattr(config, 'common_functions'):
        logger.error('common_functions  not specified.')
        exit(1)

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    package_url='https://openwhisk.ng.bluemix.net/api/v1/namespaces/' + config.cloudfunctions_namespace.replace('@', '%40') + '/packages/' + config.cloudfunctions_package+ '?overwrite=true'
    response = requests.put(package_url, auth=(config.cloudfunctions_username, config.cloudfunctions_password), headers={'Content-Type': 'application/json'}, data='{}')
    responseJson = response.json()
    if 'error' in responseJson:
        logger.error('Cannot create cloud functions package')
        logger.error(responseJson['error'])
        if VERBOSE: logger.info("%s", responseJson)
        sys.exit(1)
    else:
        logger.info('Cloud functions package successfully uploaded')

    filesAtPath = getFilesAtPath(config.common_functions)

    for functionFileName in filesAtPath:
        fname=os.path.basename(functionFileName)
        function_url = 'https://openwhisk.ng.bluemix.net/api/v1/namespaces/' + config.cloudfunctions_namespace + '/actions/' + config.cloudfunctions_package + '/' + fname + '?overwrite=true'
        code = open(os.path.join(config.common_functions, functionFileName), 'r').read()
        payload = {"exec": {"kind": "nodejs:default", "code": code}}

        response = requests.put(function_url, auth=(config.cloudfunctions_username, config.cloudfunctions_password),
                                headers={'Content-Type': 'application/json'}, data=json.dumps(payload), verify=False)
        responseJson = response.json()
        if 'error' in responseJson:
            logger.error('Cannot create cloud function')
            logger.error(responseJson['error'])
            if VERBOSE: logger.info("%s", responseJson)
            sys.exit(1)
        else:
            logger.info('Cloud functions %s successfully uploaded.', functionFileName)

    logger.info('FINISHING: ' + os.path.basename(__file__))
