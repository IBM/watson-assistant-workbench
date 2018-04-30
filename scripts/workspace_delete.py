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

import sys, argparse, requests, configparser
from wawCommons import printf, eprintf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deletes Bluemix conversation service workspace and deletes workspace id from config file.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('config', help='file containing section \'[conversation]\' with workspaces url=\'<url>\', conversation version=\'<version>\', username=\'<username>\', password=\'<password>\' and workspace_id=\'<workspace_id>\' ')
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
        workspaceId = config.get(conversationSection, 'workspace_id')
        printf('WCS WORKSPACE_ID: %s\n', workspaceId)
        workspacesUrl += '/' + workspaceId
    except IOError:
        eprintf('ERROR: Cannot load config file %s\n', args.config)
        sys.exit(1)

    # delete workspace
    workspacesUrl += '?version=' + version
    response = requests.delete(workspacesUrl, auth=(username, password), headers={'Accept': 'text/html'})
    responseJson = response.json()

    # check errors during upload
    if 'error' in responseJson:
        eprintf('Cannot delete conversation workspace\nERROR: %s\n', responseJson['error'])
        sys.exit(1)
    if response.status_code == 200:
        printf('Workspace was successfully deleted\n')
    else:
        eprintf('ERROR: Error while deleting workspace, status code %s\n', response.status_code)
        sys.exit(1)

    # delete workspaceId from config file
    config.remove_option(conversationSection, 'workspace_id')
    with open(args.config, 'wb') as configFile:
        config.write(configFile)
