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
from collections import defaultdict
from wawCommons import setLoggerConfig, getScriptLogger,  toIntentName, toEntityName
import logging


logger = getScriptLogger(__file__)

if __name__ == '__main__':
    setLoggerConfig()
    parser = argparse.ArgumentParser(description='convert NLU tsv files into domain-entity and intent-entity mappings.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('entitiesDir', help='directory with entities files - all of them will be included in output list if specified')
    # optional arguments
    parser.add_argument('-is', '--sentences', help='.tsv file in NLU format with tagged entities in example sentences in third column and intent names in second column')
    parser.add_argument('-l', '--list', required=False, help='output file with list of all entities (if it should be generated)')
    parser.add_argument('-d', '--domEnt', required=False, help='output file with domain-entity mapping (if it should be generated)')
    parser.add_argument('-i', '--intEnt', required=False, help='output file with intent-entity mapping (if it should be generated)')
    parser.add_argument('-ni', '--common_intents_nameCheck', action='append', nargs=2, help="regex and replacement for intent name check, e.g. '-' '_' for to replace hyphens for underscores or '$special' '\L' for lowercase")
    parser.add_argument('-ne', '--common_entities_nameCheck', action='append', nargs=2, help="regex and replacement for entity name check, e.g. '-' '_' for to replace hyphens for underscores or '$special' '\L' for lowercase")
    parser.add_argument('-s', '--soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    VERBOSE = args.verbose
    NAME_POLICY = 'soft' if args.soft else 'hard'

    domEntMap = defaultdict(dict)
    intEntMap = defaultdict(dict)

    if args.sentences:
        with open(args.sentences, "r") as sentencesFile:
            for line in sentencesFile.readlines():
                line = line.rstrip()
                if not line: continue
                intentName = toIntentName(NAME_POLICY, args.common_intents_nameCheck, line.split("\t")[1])
                intentText = line.split("\t")[2]
                intentSplit = intentName.split("_",1)
                domainPart = intentSplit[0]
                intentPart = intentSplit[1]
                for entity in re.findall('<([^>]+)>[^<]+<\/[^>]+>', intentText):
                    domEntMap[domainPart][entity] = 1
                    intEntMap[intentPart][entity] = 1

    if args.domEnt:
        with open(args.domEnt, 'w') as domEntFile:
            for domain in sorted(domEntMap.keys()):
                entities="NONE;"
                for entity in sorted(domEntMap[domain].keys()):
                    entities += entity + ";"
                domEntFile.write(domain + ";" + entities + "\n")
        if VERBOSE: logger.info("Domain-entity map '%s' was successfully created", args.domEnt)

    if args.domEnt:
        with open(args.intEnt, 'w') as intEntFile:
            for intent in sorted(intEntMap.keys()):
                entities="NONE;"
                for entity in sorted(intEntMap[intent].keys()):
                    entities += entity + ";"
                intEntFile.write(intent + ";" + entities + "\n")
        if VERBOSE: logger.info("Intent-entity map '%s' was successfully created", args.domEnt)

    if args.list:
        with open(args.list, 'w') as listFile:
            # process entities
            entityNames = []
            for entityFileName in os.listdir(args.entitiesDir):
                entityName = toEntityName(NAME_POLICY, args.common_entities_nameCheck , os.path.splitext(entityFileName)[0])
                if entityName not in entityNames:
                    entityNames.append(entityName)
            for entityName in entityNames:
                listFile.write(entityName + ";\n")
        if VERBOSE: logger.info("Entities list '%s' was successfully created", args.list)
