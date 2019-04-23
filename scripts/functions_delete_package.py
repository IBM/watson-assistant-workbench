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
from wawCommons import setLoggerConfig, getScriptLogger, getFilesAtPath, openFile, getRequiredParameter, getOptionalParameter, getParametersCombination, convertApikeyToUsernameAndPassword, errorsInResponse
import urllib3
import logging


logger = getScriptLogger(__file__)

def main(argv):
    """Deletes the cloudfunctions package specified in the configuration file or as CLI argument."""
    parser = argparse.ArgumentParser(description="Deletes cloud functions package.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('-c', '--common_configFilePaths', help="configuration file", action='append')
    parser.add_argument('--common_functions', required=False, help="directory where the cloud functions are located")
    parser.add_argument('--cloudfunctions_namespace', required=False, help="cloud functions namespace")
    parser.add_argument('--cloudfunctions_apikey', required=False, help="cloud functions apikey")
    parser.add_argument('--cloudfunctions_username', required=False, help="cloud functions user name")
    parser.add_argument('--cloudfunctions_password', required=False, help="cloud functions password")
    parser.add_argument('--cloudfunctions_package', required=False, help="cloud functions package name")
    parser.add_argument('--cloudfunctions_url', required=False, help="url of cloud functions API")
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))

    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    def handleResponse(response):
        """Get response code and show an error if it's not OK"""
        code = response.status_code
        if code != requests.codes.ok:
            if code == 401:
                logger.error("Authorization error. Check your credentials. (Error code " + str(code) + ")")
            elif code == 403:
                logger.error("Access is forbidden. Check your credentials and permissions. (Error code " + str(code) + ")")
            elif code == 404:
                logger.error("The resource could not be found. Check your cloudfunctions url and namespace. (Error code " + str(code) + ")")
            elif code >= 500:
                logger.error("Internal server error. (Error code " + str(code) + ")")
            else:
                logger.error("Unexpected error code: " + str(code) + ")")

            errorsInResponse(response.json())
            return False
        return True

    def isActionSequence(action):
        for annotation in action['annotations']:
            if 'key' in annotation and annotation['key'] == 'exec':
                if 'value' in annotation and annotation['value'] == 'sequence':
                    return True;
        return False

    config = Cfg(args)
    logger.info('STARTING: '+ os.path.basename(__file__))

    namespace = getRequiredParameter(config, 'cloudfunctions_namespace')
    auth = getParametersCombination(config, 'cloudfunctions_apikey', ['cloudfunctions_password', 'cloudfunctions_username'])
    package = getRequiredParameter(config, 'cloudfunctions_package')
    namespaceUrl = getRequiredParameter(config, 'cloudfunctions_url')
    functionDir = getRequiredParameter(config, 'common_functions')

    if 'cloudfunctions_apikey' in auth:
        username, password = convertApikeyToUsernameAndPassword(auth['cloudfunctions_apikey'])
    else:
        username = auth['cloudfunctions_username']
        password = auth['cloudfunctions_password']

    logger.info("Will delete cloud functions in package '" + package + "'.")

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    packageUrl = namespaceUrl + '/' + namespace + '/packages/' + package
    response = requests.get(packageUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
    if not handleResponse(response):
        logger.critical("Unable to get information about package '" + package + "'.")
        sys.exit(1)

    actions = response.json()['actions']
    # put the sequences at the beggining
    actions.sort(key=lambda action: isActionSequence(action))

    for action in actions:
        name = action['name']
        actionUrl = namespaceUrl + '/' + namespace + '/actions/' + package + '/' + name
        logger.verbose("Deleting action '" + name + "' at " + actionUrl)
        response = requests.delete(actionUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
        if not handleResponse(response):
            logger.critical("Unable to delete action " + name + "' at " + actionUrl)
            sys.exit(1)
        logger.verbose("Action deleted.")

    logger.verbose("Deleting package '" + package + "' at " + packageUrl)
    response = requests.delete(packageUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
    if not handleResponse(response):
        logger.critical("Unable to delete package '" + package + "' at " + packageUrl)
        sys.exit(1)
    logger.verbose("Package deleted.")
    logger.info("Cloud functions in package successfully deleted.")

if __name__ == '__main__':
    main(sys.argv[1:])
