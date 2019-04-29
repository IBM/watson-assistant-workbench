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
from wawCommons import setLoggerConfig, getScriptLogger, getFilesAtPath, openFile, getRequiredParameter, getOptionalParameter, getParametersCombination, convertApikeyToUsernameAndPassword, errorsInResponse
from urllib.parse import quote
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

def main(argv):
    # parse sequence names - because we need to get the name first and
    # then create corresponding arguments for the main parser
    sequenceSubparser = argparse.ArgumentParser()
    sequenceSubparser.add_argument('--cloudfunctions_sequences', nargs='+')
    argvWithoutHelp = list(argv)
    if "--help" in argv: argvWithoutHelp.remove("--help")
    if "-h" in argv: argvWithoutHelp.remove("-h")
    sequenceNames = sequenceSubparser.parse_known_args(argvWithoutHelp)[0].cloudfunctions_sequences or []

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
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    parser.add_argument('--cloudfunctions_sequences', nargs='+', required=False, help="cloud functions sequence names")

    for runtime in list(interpretedRuntimes.values()) + list(compiledRuntimes.values()):
        parser.add_argument('--cloudfunctions_' + runtime + '_version', required=False,
            help="cloud functions " + runtime + " version")

    # Add arguments for each sequence to be able to define the functions in the sequence
    for sequenceName in sequenceNames:
        try:
            parser.add_argument("--cloudfunctions_sequence_" + sequenceName, required=True, help="functions in sequence '" + sequenceName + "'")
        except argparse.ArgumentError as e:
            if "conflicting option" in str(e):
                # from None is needed in order to show only the custom exception and not the whole traceback
                # (It would read as 'During handling of the above exception, another exception has occurred', but we DID handle it)
                raise argparse.ArgumentError(None, "Duplicate sequence name: "+sequenceName) from None
            else:
                raise e

    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    logger.info('STARTING: '+ os.path.basename(__file__))

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
            elif code == 408:
                logger.error("Request Timeout. (Error code " + str(code) + ")")
            elif code >= 500:
                logger.error("Internal server error. (Error code " + str(code) + ")")
            else:
                logger.error("Unexpected error code: " + str(code))

            errorsInResponse(response.json())
            return False
        return True

    config = Cfg(args)

    namespace = getRequiredParameter(config, 'cloudfunctions_namespace')
    urlNamespace = quote(namespace)
    auth = getParametersCombination(config, 'cloudfunctions_apikey', ['cloudfunctions_password', 'cloudfunctions_username'])
    package = getRequiredParameter(config, 'cloudfunctions_package')
    cloudFunctionsUrl = getRequiredParameter(config, 'cloudfunctions_url')
    functionDir = getRequiredParameter(config, 'common_functions')
    # If sequence names are already defined (from console), do nothing. Else look for them in the configuration.
    if not sequenceNames:
        sequenceNames = getOptionalParameter(config, 'cloudfunctions_sequences') or []
    # SequenceNames has to be a list
    if type(sequenceNames) is str:
        sequenceNames = [sequenceNames]
    # Create a dict of {<seqName>: [<functions 1>, <function2> ,...]}
    sequences = {seqName: getRequiredParameter(config, "cloudfunctions_sequence_" + seqName) for seqName in sequenceNames}

    if 'cloudfunctions_apikey' in auth:
        username, password = convertApikeyToUsernameAndPassword(auth['cloudfunctions_apikey'])
    else:
        username = auth['cloudfunctions_username']
        password = auth['cloudfunctions_password']

    runtimeVersions = {}
    for ext, runtime in list(interpretedRuntimes.items()) + list(compiledRuntimes.items()):
        runtimeVersions[runtime] = runtime + ':' + getattr(config, 'cloudfunctions_' + runtime + '_version', 'default')

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    packageUrl = cloudFunctionsUrl + '/' + urlNamespace + '/packages/' + package + '?overwrite=true'
    logger.info("Will create cloudfunctions package %s.", package)
    response = requests.put(packageUrl, auth=(username, password), headers={'Content-Type': 'application/json'},
                            data='{}')
    if not handleResponse(response):
        logger.critical("Cannot create cloud functions package %s.", package)
        sys.exit(1)
    else:
        logger.info('Cloud functions package successfully uploaded')

    filesAtPath = getFilesAtPath(functionDir, ['*' + ext for ext in (list(interpretedRuntimes) +
                                                                     list(compiledRuntimes) +
                                                                     compressedFiles)])

    logger.info("Will deploy functions at paths %s.", functionDir)

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

        functionUrl = cloudFunctionsUrl + '/' + urlNamespace + '/actions/' + package + '/' + funcName + '?overwrite=true'

        if binary:
            content = base64.b64encode(open(functionFilePath, 'rb').read()).decode('utf-8')
        else:
            content = open(functionFilePath, 'r').read()
        payload = {'exec': {'kind': runtimeVersions[runtime], 'binary': binary, 'code': content}}

        logger.verbose("Deploying function %s", funcName)
        response = requests.put(functionUrl, auth=(username,password), headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload), verify=False)
        if not handleResponse(response):
            logger.critical("Cannot deploy cloud function %s.", funcName)
            sys.exit(1)
        else:
            logger.verbose('Cloud function %s successfully deployed.', funcName)
    logger.info("Cloudfunctions successfully deployed.")

    if sequences:
        logger.info("Will deploy cloudfunction sequences.")

    for seqName in sequences:
        sequenceUrl = cloudFunctionsUrl + '/' + urlNamespace + '/actions/' + package + '/' + seqName + '?overwrite=true'
        functionNames = sequences[seqName]
        fullFunctionNames = [namespace + '/' + package +'/' + functionName for functionName in functionNames]
        payload = {'exec': {'kind': 'sequence', 'binary': False, 'components': fullFunctionNames}}
        logger.verbose("Deploying cloudfunctions sequence '%s': %s", seqName, functionNames)
        response = requests.put(sequenceUrl, auth=(username, password), headers={'Content-Type': 'application/json'},
                                    data=json.dumps(payload), verify=False)
        if not handleResponse(response):
            logger.critical("Cannot deploy cloudfunctions sequence %s", seqName)
            sys.exit(1)
        else:
            logger.verbose("Sequence '%s' deployed.", seqName)
    if sequences:
        logger.info("Cloudfunction sequences successfully deployed.")
    logger.info('FINISHING: ' + os.path.basename(__file__))

def _getZipPackageType(zipFilePath):
    with zipfile.ZipFile(zipFilePath, 'r') as functionsZip:
        for zipMember in functionsZip.namelist():
            for item in zipContent:
                if zipMember.endswith(item):
                    return zipContent[item]
    return None

if __name__ == '__main__':
    main(sys.argv[1:])
