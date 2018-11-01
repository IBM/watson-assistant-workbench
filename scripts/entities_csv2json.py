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

import json,sys,argparse,os
import io
from cfgCommons import Cfg
from wawCommons import printf, eprintf, toEntityName, getFilesAtPath

if __name__ == '__main__':
    printf('\nSTARTING: ' + os.path.basename(__file__) + '\n')
    parser = argparse.ArgumentParser(description='Conversion entity csv files to .json.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration fil, the optional name of file where configuration is stored.')
    parser.add_argument('-ie', '--common_entities', help='directory with entity csv files to be processed (all of them will be included in output json)', action='append') #-ge is functionsally equivalent to -ie
    parser.add_argument('-ge', '--common_generated_entities', help='directory with generated entity csv files to be processed (all of them will be included in output json)', action='append')
    parser.add_argument('-od', '--common_outputs_directory', required=False, help='directory where the otputs will be stored (outputs is default)')
    parser.add_argument('-oe', '--common_outputs_entities', help='file with output json with all the entities')
    parser.add_argument('-ne', '--common_entities_nameCheck', action='append', nargs=2, help="regex and replacement for entity name check, e.g. '-' '_' for to replace hyphens for underscores or '$special' '\L' for lowercase")
    parser.add_argument('-v','--common_verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('-s', '--common_soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    args = parser.parse_args(sys.argv[1:])
    config = Cfg(args)
    VERBOSE = hasattr(config, 'common_verbose')
    NAME_POLICY = 'soft' if args.common_soft else 'hard'

    if not hasattr(config, 'common_entities'):
        print('entities parameter is not defined.')
        exit(1)
    if not hasattr(config, 'common_generated_entities'):
        print('generated_entities parameter is not defined, ignoring')
    if not hasattr(config, 'common_outputs_entities'):
        print('Outputs_entities parameter is not defined, output will be generated to console.')

    # process entities
    entitiesJSON = []

    pathList = getattr(config, 'common_entities')
    if hasattr(config, 'common_generated_entities'):
        pathList = pathList + getattr(config, 'common_generated_entities')

    filesAtPath = getFilesAtPath(pathList)
    for entityFileName in sorted(filesAtPath):

        with io.open(entityFileName, mode='r', encoding='utf8') as entityFile:

            entityName = os.path.splitext(os.path.basename(entityFileName))[0]

            # system entities
            if entityName == "system_entities":
                for line in entityFile.readlines():
                    # remove comments
                    line = line.split('#')[0]
                    line = line.rstrip().lower()
                    if line:
                        # create new system entity
                        entityJSON = {}
                        entityJSON['entity'] = line
                        entityJSON['values'] = []
                        entitiesJSON.append(entityJSON)

            # other entities
            else:
                entityName = toEntityName(NAME_POLICY, getattr(config, 'common_entities_nameCheck') if hasattr(config, 'common_entities_nameCheck') else None, entityName)

                # create new entity
                entityJSON = {}
                entityJSON['entity'] = entityName
                valuesJSON = []
                # add all values
                for line in entityFile.readlines():
                    # remove comments
                    line = line.split('#')[0]
                    line = line.strip()
                    if line:
                        rawSynonyms = line.split(';')
                        # strip and lower all items in line
                        [x.strip().lower() for x in rawSynonyms]
                        representativeValue = rawSynonyms[0]
                        synonyms = sorted(list(set(rawSynonyms[1:])))
                        valueJSON = {}
                        if representativeValue[0] in '~':
                            # all patterns are represented by the first value without first char (~)
                            valueJSON['type'] = 'patterns'
                            valueJSON['value'] = representativeValue[1:]
                            # add all patterns
                            if len(synonyms) > 0:
                                valueJSON['patterns'] = synonyms
                        else:
                            # all synonyms are represented by the first value
                            valueJSON['value'] = representativeValue
                            # add all synonyms
                            if len(synonyms) > 0:
                                valueJSON['synonyms'] = synonyms
                        valuesJSON.append(valueJSON)
                entityJSON['values'] = valuesJSON
                entitiesJSON.append(entityJSON)

    if getattr(config, 'common_outputs_directory') and hasattr(config, 'common_outputs_entities'):
        if not os.path.exists(getattr(config, 'common_outputs_directory')):
            os.makedirs(getattr(config, 'common_outputs_directory'))
            print('Created new output directory ' + getattr(config, 'common_outputs_entities'))
        with io.open(os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_entities')), mode='w', encoding='utf-8') as outputFile:
            outputFile.write(json.dumps(entitiesJSON, indent=4, ensure_ascii=False, encoding='utf8'))
        if VERBOSE: printf("Entities json '%s' was successfully created\n", os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_entities')))
    else:
        print(json.dumps(entitiesJSON, indent=4, ensure_ascii=False).encode('utf8'))
        if VERBOSE: printf("Entities json was successfully created\n", os.path.basename(__file__))

    printf('\nFINISHING: ' + os.path.basename(__file__) + '\n')
