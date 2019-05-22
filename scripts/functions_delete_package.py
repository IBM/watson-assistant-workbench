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

import argparse
import logging
import os
import sys
from urllib.parse import quote

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from cfgCommons import Cfg
from wawCommons import (convertApikeyToUsernameAndPassword, errorsInResponse,
                        filterPackages, getOptionalParameter,
                        getParametersCombination, getRequiredParameter,
                        getScriptLogger, setLoggerConfig)

logger = getScriptLogger(__file__)

def main(argv):
    """Deletes the cloudfunctions package specified in the configuration file or as CLI argument."""
    parser = argparse.ArgumentParser(description="Deletes cloud functions package.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('-c', '--common_configFilePaths', help="configuration file", action='append')
    parser.add_argument('--cloudfunctions_namespace', required=False, help="cloud functions namespace")
    parser.add_argument('--cloudfunctions_apikey', required=False, help="cloud functions apikey")
    parser.add_argument('--cloudfunctions_username', required=False, help="cloud functions user name")
    parser.add_argument('--cloudfunctions_password', required=False, help="cloud functions password")
    parser.add_argument('--cloudfunctions_package', required=False, help="cloud functions package name")
    parser.add_argument('--cloudfunctions_package_pattern', required=False, help='regex pattern specifying a name of workspaces to be deleted')
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
                logger.error("Unexpected error code: " + str(code))

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
    urlNamespace = quote(namespace)
    auth = getParametersCombination(config, 'cloudfunctions_apikey', ['cloudfunctions_password', 'cloudfunctions_username'])
    cloudfunctionsUrl = getRequiredParameter(config, 'cloudfunctions_url')

    if 'cloudfunctions_apikey' in auth:
        username, password = convertApikeyToUsernameAndPassword(auth['cloudfunctions_apikey'])
    else:
        username = auth['cloudfunctions_username']
        password = auth['cloudfunctions_password']

    packagesUrl = cloudfunctionsUrl + '/' + urlNamespace + '/packages'
    response = requests.get(packagesUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
    if not handleResponse(response):
        logger.critical("Unable to get available packages.")
        sys.exit(1)

    matchedPackages = filterPackages(config, response.json())
    if not matchedPackages:
        # only name was provided
        if getOptionalParameter(config, 'cloudfunctions_package') and not getOptionalParameter(config, 'cloudfunctions_package_pattern'):
            logger.critical("Package not found. Check your cloudfunctions url and namespace.")
            sys.exit(1)
        # pattern was provided
        else:
            logger.info("No matching packages to delete.")
            return

    for package in matchedPackages:
        packageName = package['name']

        logger.info("Will delete cloud functions in package '" + packageName + "'.")

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        packageUrl = packagesUrl + '/' + packageName
        response = requests.get(packageUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
        if not handleResponse(response):
            logger.critical("Unable to get information about package '" + packageName + "'.")
            sys.exit(1)

        actions = response.json()['actions']
        # put the sequences at the beggining
        actions.sort(key=lambda action: isActionSequence(action))

        for action in actions:
            name = action['name']
            actionUrl = cloudfunctionsUrl + '/' + urlNamespace + '/actions/' + packageName + '/' + name
            logger.verbose("Deleting action '" + name + "' at " + actionUrl)
            response = requests.delete(actionUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
            if not handleResponse(response):
                logger.critical("Unable to delete action " + name + "' at " + actionUrl)
                sys.exit(1)
            logger.verbose("Action deleted.")

        logger.verbose("Deleting package '" + packageName + "' at " + packageUrl)
        response = requests.delete(packageUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
        if not handleResponse(response):
            logger.critical("Unable to delete package '" + packageName + "' at " + packageUrl)
            sys.exit(1)
        logger.verbose("Package deleted.")
        logger.info("Cloud functions in package %s successfully deleted.", packageName)

    if (len(matchedPackages) == 1):
        logger.info("One package has been successfully deleted.")
    else:
        logger.info("%s packages have been successfully deleted.", len(matchedPackages))

if __name__ == '__main__':
    main(sys.argv[1:])
