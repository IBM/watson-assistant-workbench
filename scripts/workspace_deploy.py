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

import os, json, sys, argparse, requests, configparser
from wawCommons import setLoggerConfig, getScriptLogger,  getWorkspaceId, errorsInResponse, getOptionalParameter, getRequiredParameter
from cfgCommons import Cfg
import datetime
import logging


logger = getScriptLogger(__file__)

try:
    unicode        # Python 2
except NameError:
    unicode = str  # Python 3

def main(argv):
    logger.info('STARTING: ' + os.path.basename(__file__))
    parser = argparse.ArgumentParser(description='Deploys  workspace in json format to Watson Conversation Service.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-of', '--common_outputs_directory', required=False, help='directory where the otputs are stored')
    parser.add_argument('-ow', '--common_outputs_workspace', required=False, help='name of the json file with workspace')
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-cu','--conversation-url', required=False, help='url of the conversation service API')
    parser.add_argument('-cv','--conversation_version', required=False, help='version of the conversation service API')
    parser.add_argument('-cn','--conversation_username', required=False, help='username of the conversation service instance')
    parser.add_argument('-cp','--conversation_password', required=False, help='password of the conversation service instance')
    parser.add_argument('-cid','--conversation_workspace_id', required=False, help='workspace_id of the application. If a workspace id is provided, previous workspace content is overwritten, otherwise a new workspace is created ')
    parser.add_argument('-wn','--conversation_workspace_name', required=False, help='name of the workspace')
    parser.add_argument('-v','--common_verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(argv)
    config = Cfg(args)
    VERBOSE = hasattr(config, 'common_verbose')

    # workspace info
    if not hasattr(config, 'common_outputs_directory') or not getattr(config, 'common_outputs_directory'):
        logger.error('common_outputs_directory parameter not defined.')
        exit(1)
    if not hasattr(config, 'common_outputs_workspace') or not getattr(config, 'common_outputs_workspace'):
        logger.error('common_outputs_workspace parameter not defined.')
        exit(1)
    try:
        workspaceFilePath = os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_workspace'))
        with open(workspaceFilePath, 'r') as workspaceFile:
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
    workspaceId = getWorkspaceId(config, workspacesUrl, version, username, password)
    if workspaceId:
        logger.info("Updating existing workspace.")
    else:
        logger.info("Creating new workspace.")

    requestUrl = workspacesUrl + '/' + workspaceId + '?version=' + version

    # create/update workspace
    response = requests.post(requestUrl, auth=(username, password), headers={'Content-Type': 'application/json'}, data=json.dumps(workspace, indent=4))
    responseJson = response.json()

    if VERBOSE: logger.info("response: %s", responseJson)
    if not errorsInResponse(responseJson):
        logger.info('Workspace successfully uploaded.')
    else:
        logger.error('Cannot upload workspace.')
        sys.exit(1)

    if not hasattr(config, 'conversation_workspace_id') or not getattr(config, 'conversation_workspace_id'):
        setattr(config, 'conversation_workspace_id', responseJson['workspace_id'])
        logger.info('WCS WORKSPACE_ID: %s', responseJson['workspace_id'])
    if hasattr(config, 'common_output_config'):
        config.saveConfiguration(getattr(config, 'common_output_config'))

    if hasattr(config, 'context_client_name'):
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
    if hasattr(config, 'common_outputs_client') and getattr(config, 'common_outputs_client'):
        clientFilePath = os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_client'))
        if hasattr(config, 'context_client_name'):
            try:
                with open(clientFilePath, "w") as clientFile:
                    clientFile.write('<meta http-equiv="refresh" content=\"0; url=' + clientv2URL + '\" />')
                    clientFile.write('<p><a href=\"' + clientv2URL + '\">Redirect</a></p>')
                clientFile.close()
            except IOError:
                logger.error('Cannot write to %s', clientFilePath)
                sys.exit(1)

    logger.info('FINISHING: '+ os.path.basename(__file__))

if __name__ == '__main__':
    setLoggerConfig()
    main(sys.argv[1:])

