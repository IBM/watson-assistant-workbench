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

# coding: utf-8
import sys, argparse, os, codecs
from cfgCommons import Cfg
from wawCommons import printf
from XLSXHandler import XLSXHandler
from XMLHandler import XMLHandler

from wawCommons import printf, eprintf

def saveDialogDataToFileSystem(dialogData, handler, config):
    if hasattr(config, 'common_generated_dialogs') and not os.path.exists(getattr(config, 'common_generated_dialogs')):
        os.makedirs(getattr(config, 'common_generated_dialogs'))
        print('Created new directory ' + getattr(config, 'common_generated_dialogs'))

    domains = dialogData.getDomains()
    for domain in domains:
        filename = getattr(config, 'common_generated_dialogs') + '/' + domain + '.xml'
        with codecs.open(filename, 'w', encoding='utf8') as dialogFile:
            xmlData = handler.convertDialogData(dialogData, domains[domain])
            dialogFile.write(handler.printXml(xmlData))

    if hasattr(config, 'common_generated_intents') and not os.path.exists(getattr(config, 'common_generated_intents')[0]):
        os.makedirs(getattr(config, 'common_generated_intents')[0])
        print('Created new directory ' + getattr(config, 'common_generated_intents')[0])

    for intent, intentData in dialogData.getAllIntents().iteritems():
        if len(intentData.getIntentAlternatives()) > 0:
            with open(os.path.join(getattr(config, 'common_generated_intents')[0], intent.decode('utf8') + '.csv'), 'w') as intentFile:
                for alternative in intentData.getIntentAlternatives():
                    intentFile.write(alternative.encode('utf8') + '\n')

    if hasattr(config, 'common_generated_entities') and not os.path.exists(getattr(config, 'common_generated_entities')[0]):
        os.makedirs(getattr(config, 'common_generated_entities')[0])
        print('Created new directory ' + getattr(config, 'common_generated_entities')[0])

    entities = dialogData.getAllEntities()
    for entity in entities:
        with open(os.path.join(getattr(config, 'common_generated_entities')[0], entity.encode('ascii', 'ignore') + '.csv'), 'w') as entityFile:
            for entityList in entities[entity]:
                entityFile.write(entityList.encode('utf8') + '\n')

if __name__ == '__main__':
    printf('\nSTARTING: ' + os.path.basename(__file__) + '\n')
    parser = argparse.ArgumentParser(description='Creates dialog nodes with answers to intents .', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # optional arguments
    parser.add_argument('-x', '--common_xls', required=False, help='file with MSExcel formated dialog', action='append')
    parser.add_argument('-gd', '--common_generated_dialogs', nargs='?', help='generated dialog file')
    parser.add_argument('-gi', '--common_generated_intents', nargs='?', help='directory for generated intents')
    parser.add_argument('-ge', '--common_generated_entities', nargs='?', help='directory for generated entities')
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-v', '--common_verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    config = Cfg(args)
    VERBOSE = hasattr(config, 'common_verbose')

    if hasattr(config, 'common_verbose') and getattr(config, 'common_verbose'):
        name_policy = 'soft_verbose'
    if not hasattr(config, 'common_xls'):
        eprintf('ERROR: xls is not defined')
        exit(1)
    if not hasattr(config, 'common_generated_dialogs'):
        if VERBOSE: printf('INFO: generated_dialogs parameter is not defined\n')
    if not hasattr(config, 'common_generated_intents'):
        if VERBOSE: printf('INFO: generated_intents parameter is not defined\n')
    if not hasattr(config, 'common_generated_entities'):
        if VERBOSE: printf('INFO: generated_entities parameter is not defined\n')

    xlsxHandler = XLSXHandler()
    allDataBlocks = {}  # map of datablocks, key: Excel sheet name, value: list of all block in the sheet

    print(getattr(config, 'common_xls'))
    for fileOrFolder in getattr(config, 'common_xls'):
        if VERBOSE: printf('INFO: Searching in path: %s\n', fileOrFolder)
        if os.path.isdir(fileOrFolder):
            xlsDirList = os.listdir(fileOrFolder)
            for xlsFile in xlsDirList:
                if os.path.isfile(os.path.join(fileOrFolder, xlsFile)) and xlsFile.endswith('.xlsx') and \
                        not(xlsFile.startswith('~')) and not(xlsFile.startswith('.')):
                    xlsxHandler.parseXLSXIntoDataBlocks(fileOrFolder + "/" + xlsFile)
                else:
                    eprintf('WARNING: The file %s skipped due to failing file selection policy check. '
                            'It should be .xlsx file not starting with ~ or .(dot).\n', os.path.join(fileOrFolder, xlsFile))

        elif os.path.exists(fileOrFolder):
            xlsxHandler.parseXLSXIntoDataBlocks(fileOrFolder)

    xlsxHandler.convertBlocksToDialogData()
    saveDialogDataToFileSystem(xlsxHandler.getDialogData(), XMLHandler(), config)

    printf('\nFINISHING: ' + os.path.basename(__file__) + '\n')
