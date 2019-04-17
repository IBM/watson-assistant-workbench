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

import sys, argparse, requests, configparser, os
from wawCommons import setLoggerConfig, getScriptLogger, openFile, getOptionalParameter, getRequiredParameter, filterWorkspaces, getWorkspaces, errorsInResponse
from cfgCommons import Cfg
import logging


logger = getScriptLogger(__file__)

def main(argv):
    logger.info('STARTING: ' + os.path.basename(__file__))
    parser = argparse.ArgumentParser(description='Deletes Bluemix conversation service workspace and deletes workspace id from config file.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-cu','--conversation_url', required=False, help='url of the conversation service API')
    parser.add_argument('-cv','--conversation_version', required=False, help='version of the conversation service API')
    parser.add_argument('-cn','--conversation_username', required=False, help='username of the conversation service instance')
    parser.add_argument('-cp','--conversation_password', required=False, help='password of the conversation service instance')
    parser.add_argument('-cid','--conversation_workspace_id', required=False, help='workspace_id of the application.')
    parser.add_argument('-wn','--conversation_workspace_name', required=False, help='name of the workspace')
    parser.add_argument('-wnm','--conversation_workspace_match_by_name', required=False, help='true if the workspace name should be matched by name (or pattern if defined)')
    parser.add_argument('-wnp','--conversation_workspace_name_pattern', required=False, help='regex pattern specifying a name of workspaces to be deleted')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    config = Cfg(args)

    # load credentials
    version = getRequiredParameter(config, 'conversation_version')
    workspacesUrl = getRequiredParameter(config, 'conversation_url')
    username = getRequiredParameter(config, 'conversation_username')
    password = getRequiredParameter(config, 'conversation_password')
    try:
        workspaces = filterWorkspaces(config, getWorkspaces(workspacesUrl, version, username, password))
    except SystemExit as e:
        logger.error("Failed to retrieve workspaces to delete.")
        sys.exit(1)

    nWorkspacesDeleted = 0
    for workspace in workspaces:
        # delete workspace
        requestUrl = workspacesUrl + '/' + workspace['workspace_id'] + '?version=' + version
        response = requests.delete(requestUrl, auth=(username, password), headers={'Accept': 'text/html'})
        responseJson = response.json()
        # check errors during upload
        errorsInResponse(responseJson)

        if response.status_code == 200:
            nWorkspacesDeleted += 1
            logger.info("Workspace '%s' was successfully deleted", workspace['name'])
            # delete workspaceId from config file
            if hasattr(config, 'conversation_workspace_id'):
                delattr(config, 'conversation_workspace_id')
        elif response.status_code == 400:
            logger.error("Error while deleting workspace  '%s', status code '%s' (invalid request)", workspace['name'], response.status_code)
            sys.exit(1)
        else:
            logger.error("Error while deleting workspace  '%s', status code '%s'", workspace['name'], response.status_code)
            sys.exit(1)

    if not nWorkspacesDeleted:
        logger.info("No workspace has been deleted")
    elif nWorkspacesDeleted == 1:
        logger.info("One workspace has been successfully deleted")
    else:
        logger.info(f"{nWorkspacesDeleted} workspaces have been successfully deleted")

    outputConfigFile = getOptionalParameter(config, 'common_output_config')
    if outputConfigFile:
        config.saveConfiguration(outputConfigFile)
        logger.info("Configuration was saved to %s", outputConfigFile)

if __name__ == '__main__':
    main(sys.argv[1:])
