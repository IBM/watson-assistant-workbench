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

import json, sys, time, argparse, requests, configparser
from wawCommons import printf, eprintf

CHECK_MESSAGES_TIME_MAX = 5 # in seconds
CHECK_WORKSPACE_TIME_DELAY = 1 # in seconds
CHECK_WORKSPACE_TIME_MAX = 5 * 60 # in seconds

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tests all dialog flows from given file and save received responses to output file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('config', help='file containing section \'[conversation]\' with workspaces url=\'<url>\', conversation version=\'<version>\', username=\'<username>\', password=\'<password>\' and optionally workspace_id=\'<workspace_id>\' ')
    parser.add_argument('inputFileName', help='file with test jsons to be sent to conversation service. (One at each line at key \'input\'.)')
    parser.add_argument('outputFileName', help='file where to store received data from conversation service. (One response at each line.)')
    # optional arguments
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    VERBOSE = args.verbose

    # load config file
    conversationSection = 'conversation'
    try:
        config = configparser.ConfigParser()
        config.read(args.config)
        workspacesUrl = config.get(conversationSection, 'url')
        version = config.get(conversationSection, 'version')
        username = config.get(conversationSection, 'username')
        printf('WCS USERNAME: %s\n', username)
        password = config.get(conversationSection, 'password')
        printf('WCS PASSWORD: %s\n', password)
        workspaceId = config.get(conversationSection, 'workspace_id', fallback=None)
        if workspaceId:
            printf('WCS WORKSPACE_ID: %s\n', workspaceId)
            workspacesUrl += '/' + workspaceId
    except IOError:
        eprintf('ERROR: Cannot load config file %s\n', args.config)
        sys.exit(1)

    # wait until workspace is done with training
    checkWorkspaceTime = 0
    url = workspacesUrl + '?version=' + version
    while True:
        response = requests.get(url, auth=(username, password))
        responseJson = response.json()
        if 'error' in responseJson:
            eprintf('ERROR: %s\n', responseJson['error'])
            sys.exit(1)
        status = responseJson['status']
        printf('WCS WORKSPACE STATUS: %s\n', status)
        if status == 'Available':
            break
        else:
            # sleep some time and check messages again
            if checkWorkspaceTime > CHECK_WORKSPACE_TIME_MAX:
                eprintf('ERROR: Workspace have not become available before timeout, timeout: %d, response:\n%s\n', CHECK_MESSAGES_TIME_MAX, json.dumps(responseJson, indent=4, sort_keys=True, ensure_ascii=False).encode('utf8'))
                sys.exit(1)
            time.sleep(CHECK_WORKSPACE_TIME_DELAY)
            checkWorkspaceTime = checkWorkspaceTime + CHECK_WORKSPACE_TIME_DELAY

    # run tests
    url = workspacesUrl + '/message?version=' + version
    receivedOutputJson = []
    try:
        with open(args.inputFileName, "r") as inputFile:
            try:
                with open(args.outputFileName, "w") as outputFile:
                    first = True
                    dialogId = ""
                    # for every input line
                    for inputLine in inputFile:
                        loadedJson = json.loads(inputLine)
                        inputJson = loadedJson['input_message'] # input json for tests
                        if dialogId and dialogId == loadedJson['dialog_id']:
                            if receivedOutputJson and receivedOutputJson['context']:
                                inputJson['context'] = receivedOutputJson['context'] # use context from last dialog turn
                        dialogId = loadedJson['dialog_id']
                        response = requests.post(url, auth=(username, password), headers={'Content-Type': 'application/json'}, data=json.dumps(inputJson, indent=4, ensure_ascii=False).encode('utf8'))
                        receivedOutputJson = response.json()
                        if not first:
                            outputFile.write("\n")
                        outputFile.write(json.dumps(receivedOutputJson, ensure_ascii=False).encode('utf8'))
                        first = False
            except IOError:
                eprintf('ERROR: Cannot open test output file %s\n', args.outputFileName)
                sys.exit(1)
    except IOError:
        eprintf('ERROR: Cannot open test input file %s\n', args.inputFileName)
        sys.exit(1)
