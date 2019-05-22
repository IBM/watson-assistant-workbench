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
from __future__ import print_function

import argparse
import logging
import os
import sys

import clean_generated
import dialog_xls2xml
import dialog_xml2json
import entities_csv2json
import functions_deploy
import intents_csv2json
import workspace_addjson
import workspace_compose
import workspace_deploy
from wawCommons import getScriptLogger, setLoggerConfig

logger = getScriptLogger(__file__)

def main(argv):
    defaultParamList=['shared.cfg', 'private.cfg']

    parser = argparse.ArgumentParser(description='This script executes all the steps needed for building and deployment of the WeatherFrog application.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--config', help='configuaration file', action='append')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    logger.info('STARTING: ' + os.path.basename(__file__))
    logger.info('Using WAW directory: ' + os.path.dirname(__file__))
    logger.verbose('THIS IS VERBOSE')

    #Assemble command line parameters out of parameters or defaults
    paramsAll = []
    if hasattr(args, 'config') and args.config != None: # if config files provided - ignore defaults
        for strParamsItem in args.config:
            if os.path.isfile(strParamsItem):
                paramsAll += ['-c', strParamsItem]
            else:
                logger.error('Configuration file %s not found.', strParamsItem)
                exit(1)
    else:
        # create list of default config files
        for strParamsItem in defaultParamList:
            if os.path.isfile(strParamsItem):
                paramsAll += ['-c', strParamsItem]
            else:
                logger.warning('Default configuration file %s was not found, ignoring.', strParamsItem)
    if len(paramsAll) == 0:
        logger.error('Please provide at least one configuration file.')
        exit(1)


    #Execute all steps
    logger.verbose('python clean_generated.py '+' '.join(paramsAll))
    clean_generated.main(paramsAll)

    logger.verbose('python dialog_xls2xml.py '+' '.join(paramsAll))
    dialog_xls2xml.main(paramsAll)

    logger.verbose('python dialog_xml2json.py '+' '.join(paramsAll))
    dialog_xml2json.main(paramsAll)

    logger.verbose('python entities_csv2json.py '+' '.join(paramsAll))
    entities_csv2json.main(paramsAll)

    logger.verbose('python intents_csv2json.py '+' '.join(paramsAll))
    intents_csv2json.main(paramsAll)

    logger.verbose('python clean_generated.py '+' '.join(paramsAll))
    dialog_xml2json.main(paramsAll)

    logger.verbose('python workspace_compose.py '+' '.join(paramsAll))
    workspace_compose.main(paramsAll)

    logger.verbose('python workspace_addjson.py '+' '.join(paramsAll))
    workspace_addjson.main(paramsAll)

    logger.verbose('python workspace_deploy.py '+' '.join(paramsAll))
    workspace_deploy.main(paramsAll)

    logger.verbose('python functions_deploy.py '+' '.join(paramsAll))
    functions_deploy.main(paramsAll)

    logger.info('FINISHING: ' + os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])
