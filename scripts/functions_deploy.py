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
from wawCommons import printf, eprintf, getFilesAtPath, getRequiredParameter
import urllib3


def main(args):
    printf("\nSTARTING: %s\n", os.path.basename(__file__))
    parser = argparse.ArgumentParser(description="Deploys the cloud functions", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('-c', '--common_configFilePaths', help="configuaration file", action='append')
    parser.add_argument('--common_functions', required=False, help="directory where the cloud functions are located")
    parser.add_argument('--cloudfunctions_namespace', required=False, help="cloud functions namespace")
    parser.add_argument('--cloudfunctions_username', required=False, help="cloud functions user name")
    parser.add_argument('--cloudfunctions_password', required=False, help="cloud functions password")
    parser.add_argument('--cloudfunctions_package', required=False, help="cloud functions package name")

    extToRuntime = {
        '.js': 'nodejs',
        '.py': 'python',
        '.go': 'go',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift'
    }

    for runtime in extToRuntime.values():
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

    for ext, runtime in extToRuntime.items():
        extToRuntime[ext] = runtime + ':' + getattr(config, 'cloudfunctions_' + runtime + '_version', 'default')

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    package_url = 'https://openwhisk.ng.bluemix.net/api/v1/namespaces/' + namespace.replace('@', '%40') + '/packages/' + package + '?overwrite=true'
    response = requests.put(package_url, auth=(username, password), headers={'Content-Type': 'application/json'}, data='{}')
    responseJson = response.json()
    if 'error' in responseJson:
        eprintf("\nCannot create cloud functions package\nERROR: %s\n", responseJson['error'])
        if VERBOSE:
            printf("%s", responseJson)
        sys.exit(1)
    else:
        printf("\nCloud functions package successfully uploaded\n")

    filesAtPath = getFilesAtPath(functionDir, ['*' + ext for ext in extToRuntime.keys()])

    for functionFileName in filesAtPath:
        fname = os.path.basename(functionFileName)
        nameAndExt = os.path.splitext(fname)

        function_url = 'https://openwhisk.ng.bluemix.net/api/v1/namespaces/' + namespace + '/actions/' + package + '/' + nameAndExt[0] + '?overwrite=true'
        code = open(os.path.join(functionDir, functionFileName), 'r').read()
        payload = {'exec': {'kind': extToRuntime[nameAndExt[1]], 'code': code}}

        response = requests.put(function_url, auth=(username, password),
                                headers={'Content-Type': 'application/json'}, data=json.dumps(payload), verify=False)
        responseJson = response.json()
        if 'error' in responseJson:
            eprintf("Cannot create cloud function\nERROR: %s\n", responseJson['error'])
            if VERBOSE:
                printf("%s", responseJson)
            sys.exit(1)
        else:
            printf("Cloud functions %s successfully uploaded.\n", functionFileName)

    printf("\nFINISHING: %s\n", os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])
