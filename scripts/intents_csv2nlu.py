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

import sys, argparse, os, re
from wawCommons import setLoggerConfig, getScriptLogger,  toIntentName, toEntityName
import logging


logger = getScriptLogger(__file__)

def getEntities(entityDir, NAME_POLICY):
    """Retrieves entity value to entity name mapping from the directory with entity lists"""
    entities = {}
    for entityFileName in os.listdir(entityDir):
        entityName = toEntityName(NAME_POLICY, args.common_entities_nameCheck, os.path.splitext(entityFileName)[0])
        with open(os.path.join(args.entityDir, entityFileName), "r") as entityFile:
            for line in entityFile.readlines():
                # remove comments
                line = line.split('#')[0]
                line = line.rstrip().lower()
                for entity in line.split(';'):
                    entities[entity] = entityName
    return entities

def tagEntities(line, entities):
    """Tags entities in the text using names from the entities (entity value to entity name) dictionary"""
    newline = ""
    words = re.findall('[\w-]+', line, re.UNICODE)
    for word in words:
        if word.lower() in entities:
            line = re.sub(word, "<" + entities[word.lower()] + ">" + word + "</" + entities[word.lower()] + ">", line, re.UNICODE)
    return line

if __name__ == '__main__':
    setLoggerConfig()
    parser = argparse.ArgumentParser(description='Converts intents files to one file in NLU tsv format', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('intentsDir', help='directory with intents files - all of them will be included in output file')
    parser.add_argument('output', help='file with output intents in NLU data .tsv format')
    # optional arguments
    parser.add_argument('-e', '--entityDir', required=False, help='directory with lists of entities in csv files (file names = entity names), used to tag those entities in output')
    parser.add_argument('-l', '--list', required=False, help='file with list of all intents (if it should be generated)')
    parser.add_argument('-m', '--map', required=False, help='file with domain to intents map (if it should be generated)')
    parser.add_argument('-p', '--prefix', required=False, help='prefix for all generated intents (if it should be added)')
    parser.add_argument('-ni', '--common_intents_nameCheck', action='append', nargs=2, help="regex and replacement for intent name check, e.g. '-' '_' for to replace hyphens for underscores or '$special' '\L' for lowercase")
    parser.add_argument('-ne', '--common_entities_nameCheck', action='append', nargs=2, help="regex and replacement for entity name check, e.g. '-' '_' for to replace hyphens for underscores or '$special' '\L' for lowercase")
    parser.add_argument('-s', '--soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true', default="")
    args = parser.parse_args(sys.argv[1:])

    VERBOSE = args.verbose
    NAME_POLICY = 'soft' if args.soft else 'hard'
    PREFIX = toIntentName(NAME_POLICY, args.common_intents_nameCheck, args.prefix)

    if args.entityDir:
        entities = getEntities(args.entityDir, NAME_POLICY)

    with open(args.output, 'w') as outputFile:
        # process intents
        intentNames = []
        for intentFileName in os.listdir(args.intentsDir):
            intentName = toIntentName(NAME_POLICY, args.common_intents_nameCheck, PREFIX, os.path.splitext(intentFileName)[0])
            if intentName not in intentNames:
                intentNames.append(intentName)
            with open(os.path.join(args.intentsDir, intentFileName), "r") as intentFile:
                for line in intentFile.readlines():
                    # remove comments
                    line = line.split('#')[0]
                    if args.entityDir:
                        line = tagEntities(line, entities)
                    if line:
                        outputFile.write("1\t" + intentName + "\t" + line)
    if VERBOSE: logger.info("Intents file '%s' was successfully created", args.output)

    if args.list:
        with open(args.list, 'w') as intentsListFile:
            for intentName in intentNames:
                intentsListFile.write(intentName + "\n")
    if VERBOSE: logger.info("Intents list '%s' was successfully created", args.list)

    if args.map:
        domIntMap = {}
        for intentName in intentNames:
            intentSplit = intentName.split("_",1)
            domainPart = intentSplit[0]
            intentPart = intentSplit[1]
            if domainPart in domIntMap:
                domIntMap[domainPart] = domIntMap[domainPart] + ";" + intentPart
            else:
                domIntMap[domainPart] = ";" + intentPart
        with open(args.map, 'w') as intentsMapFile:
            for domainPart in domIntMap.keys():
                intentsMapFile.write(domainPart + domIntMap[domainPart] + "\n")
        if VERBOSE: logger.info("Domain-intent map '%s' was successfully created", args.output)
