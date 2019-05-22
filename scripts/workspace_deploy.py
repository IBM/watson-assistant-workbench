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
import datetime
import json
import logging
import os
import sys

import requests

from cfgCommons import Cfg
from wawCommons import (errorsInResponse, filterWorkspaces,
                        getOptionalParameter, getRequiredParameter,
                        getScriptLogger, getWorkspaces, openFile,
                        setLoggerConfig)

logger = getScriptLogger(__file__)

try:
    unicode        # Python 2
except NameError:
    unicode = str  # Python 3

def main(argv):
    parser = argparse.ArgumentParser(description="Deploys a workspace in json format\
     to the Watson Conversation Service. If there is no 'conversation_workspace_id' provided\
     and the 'conversation_workspace_name_unique' is set to 'true', it uploads\
     a workspace to the place specified by the 'conversation_workspace_name'",\
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-of', '--common_outputs_directory', required=False, help='directory where the otputs are stored')
    parser.add_argument('-ow', '--common_outputs_workspace', required=False, help='name of the json file with workspace')
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-cu','--conversation_url', required=False, help='url of the conversation service API')
    parser.add_argument('-cv','--conversation_version', required=False, help='version of the conversation service API')
    parser.add_argument('-cn','--conversation_username', required=False, help='username of the conversation service instance')
    parser.add_argument('-cp','--conversation_password', required=False, help='password of the conversation service instance')
    parser.add_argument('-cid','--conversation_workspace_id', required=False, help='workspace_id of the application. If a workspace id is provided, previous workspace content is overwritten, otherwise a new workspace is created ')
    parser.add_argument('-wn','--conversation_workspace_name', required=False, help='name of the workspace')
    parser.add_argument('-wnu','--conversation_workspace_name_unique', required=False, help='true if the workspace name should be unique across apecified assistant')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    config = Cfg(args)
    logger.info('STARTING: ' + os.path.basename(__file__))

    # workspace info
    try:
        workspaceFilePath = os.path.join(getRequiredParameter(config, 'common_outputs_directory'), getRequiredParameter(config, 'common_outputs_workspace'))
        with openFile(workspaceFilePath, 'r') as workspaceFile:
            workspace = json.load(workspaceFile)
    except IOError:
        logger.error('Cannot load workspace file %s', workspaceFilePath)
        sys.exit(1)
    # workspace name
    workspaceName = getOptionalParameter(config, 'conversation_workspace_name')
    if workspaceName: workspace['name'] = workspaceName
    # workspace language
    workspaceLanguage = getOptionalParameter(config, 'conversation_language')
    if workspaceLanguage: workspace['language'] = workspaceLanguage

    # credentials (required)
    username = getRequiredParameter(config, 'conversation_username')
    password = getRequiredParameter(config, 'conversation_password')
    # url (required)
    workspacesUrl = getRequiredParameter(config, 'conversation_url')
    # version (required)
    version = getRequiredParameter(config, 'conversation_version')
    # workspace id
    workspaces = filterWorkspaces(config, getWorkspaces(workspacesUrl, version, username, password))
    if len(workspaces) > 1:
        # if there is more than one workspace with the same name -> error
        logger.error('There are more than one workspace with this name, do not know which one to update.')
        exit(1)
    elif len(workspaces) == 1:
        workspaceId = workspaces[0]['workspace_id']
        logger.info("Updating existing workspace.")
    else:
        workspaceId = ""
        logger.info("Creating new workspace.")

    requestUrl = workspacesUrl + '/' + workspaceId + '?version=' + version

    # create/update workspace
    response = requests.post(requestUrl, auth=(username, password), headers={'Content-Type': 'application/json'}, data=json.dumps(workspace, indent=4))
    responseJson = response.json()

    logger.verbose("response: %s", responseJson)
    if not errorsInResponse(responseJson):
        logger.info('Workspace successfully uploaded.')
    else:
        logger.error('Cannot upload workspace.')
        sys.exit(1)

    if not getOptionalParameter(config, 'conversation_workspace_id'):
        setattr(config, 'conversation_workspace_id', responseJson['workspace_id'])
        logger.info('WCS WORKSPACE_ID: %s', responseJson['workspace_id'])

    outputConfigFile = getOptionalParameter(config, 'common_output_config')
    if outputConfigFile:
        config.saveConfiguration(outputConfigFile)

    clientName = getOptionalParameter(config, 'context_client_name')
    if clientName:
        # Assembling uri of the client
        clientv2URL='https://clientv2-latest.mybluemix.net/#defaultMinMode=true'
        clientv2URL+='&prefered_workspace_id=' + getattr(config, 'conversation_workspace_id')
        clientv2URL+='&prefered_workspace_name=' + getattr(config, 'conversation_workspace_name')
        clientv2URL+='&shared_examples_service=&url=http://zito.mybluemix.net'
        clientv2URL+='&username=' + getattr(config, 'conversation_username')
        clientv2URL+='&custom_ui.title=' + getattr(config, 'conversation_workspace_name')
        clientv2URL+='&password=' + getattr(config, 'conversation_password')
        clientv2URL+='&custom_ui.machine_img='
        clientv2URL+='&custom_ui.user_img='
        clientv2URL+='&context.user_name=' + getattr(config, 'context_client_name')
        clientv2URL+='&context.link_build_date=' + unicode(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
        clientv2URL+='&prefered_tts=none'
        clientv2URL+='&bluemix_tts.username=xx'
        clientv2URL+='&bluemix_tts.password=xx'
        clientv2URL+='&compact_mode=true'
        clientv2URL+='&compact_switch_enabled=true'
        clientv2URL+='developer_switch_enabled=false'
        logger.info('clientv2URL=%s', clientv2URL)

        # create file with automatic redirect
        clientFileName = getOptionalParameter(config, 'common_outputs_client')
        if clientFileName:
            clientFilePath = os.path.join(getRequiredParameter(config, 'common_outputs_directory'), clientFileName)
            try:
                with openFile(clientFilePath, "w") as clientFile:
                    clientFile.write('<meta http-equiv="refresh" content=\"0; url=' + clientv2URL + '\" />')
                    clientFile.write('<p><a href=\"' + clientv2URL + '\">Redirect</a></p>')
                clientFile.close()
            except IOError:
                logger.error('Cannot write to %s', clientFilePath)
                sys.exit(1)

    logger.info('FINISHING: '+ os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])
