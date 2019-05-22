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
import codecs
import json
import logging
import os
import os.path
import sys

from cfgCommons import Cfg
from wawCommons import (getRequiredParameter, getScriptLogger, replaceValue,
                        setLoggerConfig)

logger = getScriptLogger(__file__)

def main(argv):
    parser = argparse.ArgumentParser(description='This script takes a workspace JSON as one parameter and another JSON (i.e., piece of context data structure) and put the second one into desired place in the first one. This happens inplace.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # arguments
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-w','--common_outputs_workspace', required=False, help='filename of the original workspace JSON')
    parser.add_argument('-d','--common_outputs_directory', required=False, help='directory, where the workspace is located')
    parser.add_argument('-j','--includejsondata_jsonfile', required=False, help='file with JSON you want to include')
    parser.add_argument('-t','--includejsondata_targetkey', required=False, help='the key, where you want to add your JSON, i.e., "data_structure" : null; where you want to replace null, you would put "data_strucute" as this parameter')
    # optional arguments
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    #init the parameters
    args = parser.parse_args(argv)
    
    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    config = Cfg(args)

    logger.info('STARTING: ' + os.path.basename(__file__))

    # get required parameters
    # workspace
    with codecs.open(os.path.join(getRequiredParameter(config, 'common_outputs_directory'), getRequiredParameter(config, 'common_outputs_workspace')), 'r', encoding='utf8') as inputpath:
        try:
            workspaceInput = json.load(inputpath)
        except AttributeError:
            logger.error('Workspace JSON is not valid JSON: %s', os.path.join(getRequiredParameter(config, 'common_outputs_directory'), getRequiredParameter(config, 'common_outputs_workspace')))
            exit(1)
    # json to add
    with codecs.open(os.path.join(getRequiredParameter(config, 'includejsondata_jsonfile')), 'r', encoding='utf8') as jsonincludepath:
        try:
            jsonInclude = json.load(jsonincludepath)
        except AttributeError:
            logger.error('JSON to include is not valid JSON: %s', os.path.join(getRequiredParameter(config, 'includejsondata_jsonfile')))
            exit(1)
    # target element
    targetKey = getRequiredParameter(config, 'includejsondata_targetkey')

    # find the target key and add the json
    replacedValuesNumber = 0
    if 'dialog_nodes' in workspaceInput:
        workspaceInput['dialog_nodes'], replacedValuesNumber = replaceValue(workspaceInput['dialog_nodes'], targetKey, jsonInclude)
    else:
        logger.warning('Workspace does not contain \'dialog_nodes\'')

    # writing the file
    with codecs.open(os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_workspace')), 'w', encoding='utf8')  as outfile:
        json.dump(workspaceInput, outfile, indent=4)

    if replacedValuesNumber == 0:
        logger.warning('Target key not found.')
    else:
        logger.info('Writing workspaces with added JSON successfull.')

    logger.info('FINISHING: ' + os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])
