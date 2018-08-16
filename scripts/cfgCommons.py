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

import logging, configparser, sys
from wawCommons import printf, eprintf

class Cfg:

    sectionDelimiter = '_'

    def toOptionName(self, section, option):
        return section + Cfg.sectionDelimiter + option

    def __init__(self, args):
        logging.basicConfig(filename='log.log', level=logging.INFO)
        logging.info('cfg.__init__')
        self.config = {}

        # Sections (names can not contain '_')
        commonSection = 'common'
        conversationSection = 'conversation'
        cloudfunctionsSection = 'cloudfunctions'
        workspaceSection = 'workspace'
        weatherSection = 'weatherservice'
        replaceSection = 'replace'
        versionSection = 'version'
        contextSection = 'context'
        commonSection = 'common'

        # List of attributes of framework section to be appended rather then ovewrriden (if the same parameter is defined in more config files)
        frameworkAppend = ['xls', 'intents', 'entities', 'dialogs', 'functions', 'generated_intents',
                           'generated_entities', 'generated_dialog']

        if args.common_configFilePaths:
            try:
                for common_configFilePath in args.common_configFilePaths: # go over all the config files and collect all parameters
                    logging.info("Processing config file:" + common_configFilePath)
                    print("Processing config file:" + common_configFilePath)
                    configPart = configparser.ConfigParser()
                    configPart.read(common_configFilePath)
                    # Collect all attributes from all sections
                    for section in configPart.sections():
                        options = configPart.options(section)
                        for option in options:
                            optionUniqueName = self.toOptionName(section, option)
                            # value can be list
                            newValueList = configPart.get(section, option).split(',')
                            if len(newValueList) > 1: # create list
                                newValue = newValueList
                            else: # only single value
                                newValue = newValueList[0]
                            if hasattr(self, optionUniqueName):
                                warning = "WARNING: '" + optionUniqueName + " already exists. "
                                if (section == commonSection) and (option in frameworkAppend): # appended
                                    logging.debug(warning + "Appending '[" + ' '.join(newValue) +"]' to [" + ' '.join(getattr(self, optionUniqueName)) + "]");
                                    setattr(self, optionUniqueName, newValue)
                                else: # replace
                                    oldValue = getattr(self, optionUniqueName)
                                    logging.debug(warning + "Replacing '" + oldValue + "' by '[" + ' '.join(newValue) +"]'");
                                    setattr(self, optionUniqueName, newValue)
                            else:
                                if (section == commonSection) and (option in frameworkAppend): # create list
                                    setattr(self, optionUniqueName, [newValue])
                                else: # set value
                                    setattr(self, optionUniqueName, newValue)
            except IOError:
                eprintf('ERROR: Cannot load config file %s\n', args.configFileName)
                sys.exit(1)

        # Set command line parameters
        # command line parameters are having precedence, therefore they are set the last
        for arg in vars(args):
            if hasattr(args, arg) and getattr(args, arg): # attribute is present and not empty
                if hasattr(self, arg):
                    eprintf("WARNING: Overwriting config file parameter '%s' with value '%s' from comman line argumets.\n", arg, getattr(args, arg))
                setattr(self, arg, getattr(args, arg))
        if hasattr(self, 'common_output_config'):
            self.saveConfiguration(getattr(self, 'common_output_config'))

    def saveConfiguration(self, configFileName):
        outputConfig = configparser.ConfigParser()
        for optionUniqueName in self.__dict__:
            namesList = optionUniqueName.split(Cfg.sectionDelimiter)
            # find section and option names
            if len(namesList) > 1:
                section = namesList[0]
                option = Cfg.sectionDelimiter.join(namesList[1:])
            else:
                eprintf("WARNING: Missing section name in parameter name '%s', skipping.\n", optionUniqueName)
                continue
            # create non existing sections
            if not outputConfig.has_section(section):
                outputConfig.add_section(section)
            # convert types to string
            if isinstance(getattr(self, optionUniqueName), list):
                outputConfig.set(section, option, ','.join(getattr(self, optionUniqueName)))
            elif isinstance(getattr(self, optionUniqueName), bool):
                outputConfig.set(section, option, str(getattr(self, optionUniqueName)))
            else:
                outputConfig.set(section, option, getattr(self, optionUniqueName))
        try:
            with open(configFileName, 'w') as configFile:
                outputConfig.write(configFile)
        except IOError:
            eprintf('ERROR: Cannot save config file %s\n', configFileName)
