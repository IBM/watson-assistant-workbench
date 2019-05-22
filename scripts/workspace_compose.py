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
import json
import logging
import os
import sys

from cfgCommons import Cfg
from wawCommons import (getRequiredParameter, getScriptLogger, openFile,
                        setLoggerConfig)

logger = getScriptLogger(__file__)

def main(argv):
    parser = argparse.ArgumentParser(description='Concatenate intents, entities and dialogue jsons to Watson Conversation Service workspace .json format', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-of', '--common_outputs_directory', required=False, help='directory where the otputs will be stored (outputs is default)')
    parser.add_argument('-oi', '--common_outputs_intents', required=False, help='json file with intents')
    parser.add_argument('-oe', '--common_outputs_entities', required=False, help='json file with entities')
    parser.add_argument('-od', '--common_outputs_dialogs', required=False, help='json file with dialogs')
    parser.add_argument('-ox', '--common_outputs_counterexamples', required=False, help='json file with counterexamples')
    parser.add_argument('-ow', '--common_outputs_workspace', required=False, help='json file with workspace')
    parser.add_argument('-wn','--conversation_workspace_name', required=False, help='name of this workspace')
    parser.add_argument('-wl','--conversation_language', required=False, help='language of generated workspace')
    parser.add_argument('-wd','--conversation_description', required=False, help='description')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    config = Cfg(args)
    logger.info('STARTING: ' + os.path.basename(__file__))

    workspace = {}
    if hasattr(config, 'conversation_workspace_name'):
        workspace['name'] = getattr(config, 'conversation_workspace_name')
    if hasattr(config, 'conversation_language'):
        workspace['language'] = getattr(config, 'conversation_language')
    else:
        workspace['language'] = 'en'
    if hasattr(config, 'conversation_description'):
        workspace['description'] = getattr(config, 'conversation_description')

    outputsDirectory = getRequiredParameter(config, 'common_outputs_directory')

    # process intents
    intentsJSON = {}
    if hasattr(config, 'common_outputs_intents'):
        with openFile(os.path.join(outputsDirectory, getattr(config, 'common_outputs_intents')), 'r', encoding='utf8') as intentsFile:
            intentsJSON = json.load(intentsFile)
        workspace['intents'] = intentsJSON
    else:
        logger.info('output_intents not specified, omitting intents.')

    # process entities
    entitiesJSON = {}
    if hasattr(config, 'common_outputs_entities'):
        with openFile(os.path.join(outputsDirectory, getattr(config, 'common_outputs_entities')), 'r', encoding='utf8') as entitiesFile:
            entitiesJSON = json.load(entitiesFile)
        workspace['entities'] = entitiesJSON
    else:
        logger.info('output_entities not specified, omitting entities.')

    # process dialog
    dialogJSON = {}
    if hasattr(config, 'common_outputs_dialogs'):
        with openFile(os.path.join(outputsDirectory, getattr(config, 'common_outputs_dialogs')), 'r', encoding='utf8') as dialogFile:
            dialogJSON = json.load(dialogFile)
            workspace['dialog_nodes'] = dialogJSON
    else:
        logger.info('outputs_dialogs not specified, omitting dialog.')

    # process counterexamples
    intentExamplesJSON = {} # counterexamples in "intent format"
    counterexamplesJSON = [] # simple list of counterexamples ("text": "example sentence")
    if hasattr(config, 'common_outputs_counterexamples'):
        with openFile(os.path.join(outputsDirectory, getattr(config, 'common_outputs_counterexamples')), 'r', encoding='utf8') as counterexamplesFile:
            intentExamplesJSON = json.load(counterexamplesFile)
            for intentExampleJSON in intentExamplesJSON:
                counterexamplesJSON.extend(intentExampleJSON['examples'])
            workspace['counterexamples'] = counterexamplesJSON
    else:
        logger.info('outputs_counterexamples not specified, omitting counterexamples.')

    if hasattr(config, 'common_outputs_workspace'):
        with openFile(os.path.join(outputsDirectory, getattr(config, 'common_outputs_workspace')), 'w', encoding='utf8') as outputFile:
            outputFile.write(json.dumps(workspace, indent=4, ensure_ascii=False))
    else:
        logger.info('output_workspace not specified, generating to console.')

    logger.info('FINISHING: ' + os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])
