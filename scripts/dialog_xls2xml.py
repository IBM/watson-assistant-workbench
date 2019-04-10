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

# coding: utf-8
import sys, argparse, os, codecs
from cfgCommons import Cfg
from XLSXHandler import XLSXHandler
from XMLHandler import XMLHandler
from wawCommons import setLoggerConfig, getScriptLogger, openFile
import logging


logger = getScriptLogger(__file__)

def saveDialogDataToFileSystem(dialogData, handler, config):
    # Create directory for dialogs (if it does not exist already)
    if hasattr(config, 'common_generated_dialogs') and not os.path.exists(getattr(config, 'common_generated_dialogs')):
        os.makedirs(getattr(config, 'common_generated_dialogs'))
        logger.info('Created new directory ' + getattr(config, 'common_generated_dialogs'))
    # Generate xml file per dialog domain (original xls workbook (all its sheets).
    domains = dialogData.getAllDomains()
    for domain_name in domains:   # For all domains
        filename = getattr(config, 'common_generated_dialogs') + '/' + domain_name + '.xml'
        with openFile(filename, 'w', encoding='utf8') as dialogFile:
            xmlData = handler.convertDialogData(dialogData, domains[domain_name]) #process all nodes of the domain
            dialogFile.write(handler.printXml(xmlData))

    # generate intents if 'common_generated_intents' folder is specified
    if hasattr(config, 'common_generated_intents'):
        generatedIntents = getattr(config, 'common_generated_intents')
        generatedIntentsFolder = generatedIntents[0] if isinstance(generatedIntents, list) else generatedIntents
        # Create directory for intents (if it does not exist already)
        if not os.path.exists(generatedIntentsFolder):
            os.makedirs(generatedIntentsFolder)
            logger.info('Created new directory ' + generatedIntentsFolder)
        # One file per intent
        for intent, intentData in dialogData.getAllIntents().items():
            if len(intentData.getExamples()) > 0:
                intent_name = intent[1:] if intent.startswith(u'#') else intent

                with openFile(os.path.join(generatedIntentsFolder, intent_name + '.csv'), 'w') as intentFile:
                    for example in intentData.getExamples():
                        intentFile.write(example + '\n')

    # generate entities if 'common_generated_entities' folder is specified
    if hasattr(config, 'common_generated_entities'):
        generatedEntities = getattr(config, 'common_generated_entities')
        generatedEntitiesFolder = generatedEntities[0] if isinstance(generatedEntities, list) else generatedEntities
        # Create directory for entities (if it does not exist already)
        if not os.path.exists(generatedEntitiesFolder):
            os.makedirs(generatedEntitiesFolder)
            logger.info('Created new directory ' + generatedEntitiesFolder )
        # One file per entity
        for entity_name, entityData in dialogData.getAllEntities().items():
            with openFile(os.path.join(generatedEntitiesFolder, entity_name + '.csv'), 'w') as entityFile:
                for entityList in entityData.getValues():
                    entityFile.write(entityList + '\n')

def main(argv):
    parser = argparse.ArgumentParser(description='Creates dialog nodes with answers to intents .', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # optional arguments
    parser.add_argument('-x', '--common_xls', required=False, help='file with MSExcel formated dialog', action='append')
    parser.add_argument('-gd', '--common_generated_dialogs', nargs='?', help='generated dialog file')
    parser.add_argument('-gi', '--common_generated_intents', nargs='?', help='directory for generated intents')
    parser.add_argument('-ge', '--common_generated_entities', nargs='?', help='directory for generated entities')
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)
    
    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    config = Cfg(args)

    logger.info('STARTING: ' + os.path.basename(__file__))

    if hasattr(config, 'verbose') and getattr(config, 'verbose'):
        name_policy = 'soft_verbose'
    if not hasattr(config, 'common_xls'):
        logger.error('xls is not defined')
        exit(1)
    if not hasattr(config, 'common_generated_dialogs'):
        logger.verbose('generated_dialogs parameter is not defined')
    if not hasattr(config, 'common_generated_intents'):
        logger.verbose('generated_intents parameter is not defined')
    if not hasattr(config, 'common_generated_entities'):
        logger.verbose('generated_entities parameter is not defined')

    xlsxHandler = XLSXHandler(config)
    allDataBlocks = {}  # map of datablocks, key: Excel sheet name, value: list of all block in the sheet

    logger.info(getattr(config, 'common_xls'))
    for fileOrFolder in getattr(config, 'common_xls'):
        logger.verbose('Searching in path: %s', fileOrFolder)
        if os.path.isdir(fileOrFolder):
            xlsDirList = os.listdir(fileOrFolder)
            for xlsFile in xlsDirList:
                if os.path.isfile(os.path.join(fileOrFolder, xlsFile)) and xlsFile.endswith('.xlsx') and \
                        not(xlsFile.startswith('~')) and not(xlsFile.startswith('.')):
                    xlsxHandler.parseXLSXIntoDataBlocks(fileOrFolder + "/" + xlsFile)
                else:
                    logger.warning('The file %s skipped due to failing file selection policy check. '
                            'It should be .xlsx file not starting with ~ or .(dot).', os.path.join(fileOrFolder, xlsFile))

        elif os.path.exists(fileOrFolder):
            xlsxHandler.parseXLSXIntoDataBlocks(fileOrFolder)

    xlsxHandler.convertBlocksToDialogData() # Blocks-> DialogData
    xlsxHandler.updateReferences()          # Resolving cross references
    saveDialogDataToFileSystem(xlsxHandler.getDialogData(), XMLHandler(), config)

    logger.info('FINISHING: ' + os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])
