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
from wawCommons import printf, eprintf, getFilesAtPath, getRequiredParameter
import urllib3

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
    printf("\nSTARTING: %s\n", os.path.basename(__file__))
    parser = argparse.ArgumentParser(description="Deploys the cloud functions",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('-c', '--common_configFilePaths', help="configuaration file", action='append')
    parser.add_argument('--common_functions', required=False, help="directory where the cloud functions are located")
    parser.add_argument('--cloudfunctions_namespace', required=False, help="cloud functions namespace")
    parser.add_argument('--cloudfunctions_username', required=False, help="cloud functions user name")
    parser.add_argument('--cloudfunctions_password', required=False, help="cloud functions password")
    parser.add_argument('--cloudfunctions_package', required=False, help="cloud functions package name")

    for runtime in interpretedRuntimes.values() + compiledRuntimes.values():
        parser.add_argument('--cloudfunctions_' + runtime + '_version', required=False,
            help="cloud functions " + runtime + " version")

    parsedArgs = parser.parse_args(args)
    config = Cfg(parsedArgs)
    VERBOSE = parsedArgs.verbose

    namespace = getRequiredParameter(config, 'cloudfunctions_namespace')
    username = getRequiredParameter(config, 'cloudfunctions_username')
    password = getRequiredParameter(config, 'cloudfunctions_password')
    package = getRequiredParameter(config, 'cloudfunctions_package')
    functionDir = getRequiredParameter(config, 'common_functions')

    runtimeVersions = {}
    for ext, runtime in interpretedRuntimes.items() + compiledRuntimes.items():
        runtimeVersions[runtime] = runtime + ':' + getattr(config, 'cloudfunctions_' + runtime + '_version', 'default')

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    packageUrl = 'https://openwhisk.ng.bluemix.net/api/v1/namespaces/' + namespace.replace('@', '%40') + \
        '/packages/' + package + '?overwrite=true'
    response = requests.put(packageUrl, auth=(username, password), headers={'Content-Type': 'application/json'},
                            data='{}')
    responseJson = response.json()
    if 'error' in responseJson:
        eprintf("\nCannot create cloud functions package\nERROR: %s\n", responseJson['error'])
        if VERBOSE:
            printf("%s", responseJson)
        sys.exit(1)
    else:
        printf("\nCloud functions package successfully uploaded\n")


    filesAtPath = getFilesAtPath(functionDir, ['*' + ext for ext in (interpretedRuntimes.keys() + \
                                                                     compiledRuntimes.keys() + \
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
                printf("WARNING: Cannot determine function type from zip file '%s'. Skipping!\n", functionFilePath)
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
                printf("WARNING: Cannot determine function type of '%s'. Skipping!\n", functionFilePath)
                continue

        functionUrl = 'https://openwhisk.ng.bluemix.net/api/v1/namespaces/' + namespace + '/actions/' + package + \
            '/' + funcName + '?overwrite=true'

        if binary:
            content = base64.b64encode(open(os.path.join(functionDir, functionFilePath), 'rb').read())
        else:
            content = open(os.path.join(functionDir, functionFilePath), 'r').read()
        payload = {'exec': {'kind': runtimeVersions[runtime], 'binary': binary, 'code': content}}

        response = requests.put(functionUrl, auth=(username,password), headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload), verify=False)
        responseJson = response.json()
        if 'error' in responseJson:
            eprintf("Cannot create cloud function\nERROR: %s\n", responseJson['error'])
            if VERBOSE:
                printf("%s", responseJson)
            sys.exit(1)
        else:
            printf("Cloud functions %s successfully uploaded.\n", functionFilePath)

    printf("\nFINISHING: %s\n", os.path.basename(__file__))

def _getZipPackageType(zipFilePath):
    with zipfile.ZipFile(zipFilePath, 'r') as functionsZip:
        for zipMember in functionsZip.namelist():
            for item in zipContent:
                if zipMember.endswith(item):
                    return zipContent[item]
    return None

if __name__ == '__main__':
    main(sys.argv[1:])
