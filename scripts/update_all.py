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

import os, sys, logging
import subprocess, argparse
from wawCommons import printf, eprintf

if __name__ == '__main__':
    printf('\nSTARTING: ' + os.path.basename(__file__) + '\n')
    printf('\nUsing WAW directory: ' + os.path.dirname(__file__) + '\n')
    scriptsPath=os.path.dirname(__file__)
    defaultParamList=['shared.cfg', 'private.cfg']

    parser = argparse.ArgumentParser(description='This script executes all the steps needed for building and deployment of the WeatherFrog application.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--config', help='configuaration file', action='append')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    VERBOSE = args.verbose

    #Assemble command line parameters out of parameters or defaults
    paramsAll = ''
    if hasattr(args, 'config') and args.config != None: # if config files provided - ignore defaults
        for strParamsItem in args.config:
            if os.path.isfile(strParamsItem):
                paramsAll += ' -c ' + strParamsItem
            else:
                print('ERROR: Configuration file %s not found.', strParamsItem)
                exit(1)
    else:
        # create list of default config files
        for strParamsItem in defaultParamList:
            if os.path.isfile(strParamsItem):
                paramsAll += ' -c ' + strParamsItem
            else:
                print('WARNING: Default configuration file %s was not found, ignoring.', strParamsItem)
    if len(paramsAll) == 0:
        print('ERROR: Please provide at least one configuration file.', strParamsItem)
        exit(1)
    if VERBOSE:
        paramsAll += ' -v'


    #Execute all steps
    cmd = 'python ' + scriptsPath + '/clean_generated.py ' + paramsAll
    if VERBOSE:print(cmd)
    retValue = os.system(cmd)
    cmd = 'python ' + scriptsPath + '/dialog_xls2xml.py '+ paramsAll
    if VERBOSE:print(cmd)
    print(cmd)
    retValue = os.system(cmd)
    cmd = 'python ' + scriptsPath + '/dialog_xml2json.py ' + paramsAll
    if VERBOSE:print(cmd)
    retValue = os.system(cmd)
    cmd = 'python ' + scriptsPath + '/entities_csv2json.py ' + paramsAll
    if VERBOSE:print(cmd)
    retValue = os.system(cmd)
    cmd = 'python ' + scriptsPath + '/intents_csv2json.py ' + paramsAll
    if VERBOSE:print(cmd)
    retValue = os.system(cmd)
    cmd = 'python ' + scriptsPath + '/dialog_xml2json.py ' + paramsAll
    if VERBOSE:print(cmd)
    retValue = os.system(cmd)
    cmd = 'python ' + scriptsPath + '/workspace_compose.py ' + paramsAll
    if VERBOSE:print(cmd)
    retValue = os.system(cmd)
    cmd = 'python ' + scriptsPath + '/workspace_addjson.py ' + paramsAll
    if VERBOSE:print(cmd)
    retValue = os.system(cmd)

    cmd = 'python ' + scriptsPath + '/workspace_deploy.py ' + paramsAll
    if VERBOSE:print(cmd)
    retValue = os.system(cmd)
    cmd = 'python ' + scriptsPath + '/functions_deploy.py ' + paramsAll
    if VERBOSE:print(cmd)
    retValue = os.system(cmd)

    printf('\nFINISHING: ' + os.path.basename(__file__) + '\n')
