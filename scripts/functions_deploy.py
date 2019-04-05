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

import os, json, sys, argparse, requests, zipfile, base64
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from cfgCommons import Cfg
from wawCommons import setLoggerConfig, getScriptLogger, getFilesAtPath, openFile, getRequiredParameter, getOptionalParameter, getParametersCombination, convertApikeyToUsernameAndPassword
import urllib3
import logging


logger = getScriptLogger(__file__)

interpretedRuntimes = {
    '.js': 'nodejs',
    '.py': 'python',
    '.go': 'go',
    '.php': 'php',
    '.rb': 'ruby',
    '.swift': 'swift'
}

compiledRuntimes = {
# Not yet tested
#    '.jar': 'java',
#    '.zip': 'dotnet' # zip is special case
}

compressedFiles = ['.zip']

zipContent = {
    '__main__.py': 'python',
# Not yet tested
#    '.dll': 'dotnet',
#    'package.json': 'nodejs',
#    'main.rb': 'ruby',
#    'index.php': 'php'
}

def main(args):
    logger.info('STARTING: '+ os.path.basename(__file__))
    parser = argparse.ArgumentParser(description="Deploys the cloud functions",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('-c', '--common_configFilePaths', help="configuaration file", action='append')
    parser.add_argument('--common_functions', required=False, help="directory where the cloud functions are located")
    parser.add_argument('--cloudfunctions_namespace', required=False, help="cloud functions namespace")
    parser.add_argument('--cloudfunctions_apikey', required=False, help="cloud functions apikey")
    parser.add_argument('--cloudfunctions_username', required=False, help="cloud functions user name")
    parser.add_argument('--cloudfunctions_password', required=False, help="cloud functions password")
    parser.add_argument('--cloudfunctions_package', required=False, help="cloud functions package name")
    parser.add_argument('--cloudfunctions_url', required=False, help="url of cloud functions API")

    for runtime in list(interpretedRuntimes.values()) + list(compiledRuntimes.values()):
        parser.add_argument('--cloudfunctions_' + runtime + '_version', required=False,
            help="cloud functions " + runtime + " version")

    parsedArgs = parser.parse_args(args)
    config = Cfg(parsedArgs)
    VERBOSE = parsedArgs.verbose

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

    runtimeVersions = {}
    for ext, runtime in list(interpretedRuntimes.items()) + list(compiledRuntimes.items()):
        runtimeVersions[runtime] = runtime + ':' + getattr(config, 'cloudfunctions_' + runtime + '_version', 'default')

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    packageUrl = namespaceUrl + '/' + namespace + '/packages/' + package + '?overwrite=true'
    response = requests.put(packageUrl, auth=(username, password), headers={'Content-Type': 'application/json'},
                            data='{}')
    responseJson = response.json()
    if 'error' in responseJson:
        logger.error('Cannot create cloud functions package')
        logger.error(responseJson['error'])
        if VERBOSE:
            logger.info("%s", responseJson)
        sys.exit(1)
    else:
        logger.info('Cloud functions package successfully uploaded')

    filesAtPath = getFilesAtPath(functionDir, ['*' + ext for ext in (list(interpretedRuntimes) +
                                                                     list(compiledRuntimes) +
                                                                     compressedFiles)])

    for functionFilePath in filesAtPath:
        fileName = os.path.basename(functionFilePath)
        (funcName, ext) = os.path.splitext(fileName)

        runtime = None
        binary = False
        # if the file is zip, it's necessary to look inside
        if ext == '.zip':
            runtime = _getZipPackageType(functionFilePath)
            if not runtime:
                logger.warning("Cannot determine function type from zip file '%s'. Skipping!", functionFilePath)
                continue
            binary = True
        else:
            if ext in interpretedRuntimes:
                runtime = interpretedRuntimes[ext]
                binary = False
            elif ext in compiledRuntimes:
                runtime = compiledRuntimes[ext]
                binary = True
            else:
                logger.warning("Cannot determine function type of '%s'. Skipping!", functionFilePath)
                continue

        functionUrl = namespaceUrl + '/' + namespace + '/actions/' + package + '/' + funcName + '?overwrite=true'

        if binary:
            content = base64.b64encode(open(functionFilePath, 'rb').read()).decode('utf-8')
        else:
            content = open(functionFilePath, 'r').read()
        payload = {'exec': {'kind': runtimeVersions[runtime], 'binary': binary, 'code': content}}

        response = requests.put(functionUrl, auth=(username,password), headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload), verify=False)
        responseJson = response.json()
        if 'error' in responseJson:
            logger.error('Cannot create cloud function')
            logger.error(responseJson['error'])
            if VERBOSE:
                logger.info("%s", responseJson)
            sys.exit(1)
        else:
            logger.info('Cloud functions %s successfully uploaded.', functionFilePath)

    logger.info('FINISHING: ' + os.path.basename(__file__))

def _getZipPackageType(zipFilePath):
    with zipfile.ZipFile(zipFilePath, 'r') as functionsZip:
        for zipMember in functionsZip.namelist():
            for item in zipContent:
                if zipMember.endswith(item):
                    return zipContent[item]
    return None

if __name__ == '__main__':
    setLoggerConfig()
    main(sys.argv[1:])
