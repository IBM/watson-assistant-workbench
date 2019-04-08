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

import json, sys, argparse, os, glob, codecs, re
from wawCommons import setLoggerConfig, getScriptLogger,  getFilesAtPath, toIntentName, openFile
from cfgCommons import Cfg
import logging

logger = getScriptLogger(__file__)

def processExample(line, intentName, examples):
    example = {}
    #find all matches of contextual entities
    matches = re.findall(r'<(.*)>([^</>]*?)<\/\1>', line)

    #strip the tags
    lineRemovedInnerAnnotation = line
    while True:
        lineRemovedInnerAnnotation = re.sub(r'<(.*)>([^</>]*?)<\/\1>', r'\2', lineRemovedInnerAnnotation)
        outerTagsMatches = re.findall(r'<(.*)>([^</>]*?)<\/\1>', lineRemovedInnerAnnotation)
        if len(outerTagsMatches) > 0:
            for match in outerTagsMatches:
                logger.warning('For the intent %s, omitting outer tag annotation: <%s>', intentName, match[0])
        else:
            break
    invalidAnnotation = re.findall(r'<.*?>', lineRemovedInnerAnnotation)
    if len(invalidAnnotation) > 0:
        for match in invalidAnnotation:
            logger.error('Invalid annotation tag for the intent %s, %s', intentName, match)
        exit(1)

    #isn't it already in example?
    alreadyin = False
    for prevexample in examples:
        if lineRemovedInnerAnnotation == str(prevexample['text']):
            logger.warning('Example used twice for the intent %s, omitting: %s', intentName, lineRemovedInnerAnnotation)
            alreadyin = True
    if alreadyin:
        return None
    if not lineRemovedInnerAnnotation:
        logger.warning('Omitting empty line for intent %s after annotation tags are removed: %s', intentName, line)
        return None

    # locating the match
    example['text'] = lineRemovedInnerAnnotation
    if len(matches) > 0:
        example['mentions'] = []
        for match in matches:
            start = lineRemovedInnerAnnotation.index(match[1])
            end = start + len(match[1])
            entity = match[0]
            example['mentions'].append({'entity': entity, 'location':[start, end]})
    #return the example object
    return example

def main(argv):
    parser = argparse.ArgumentParser(description='Converts intent csv files to .json format of Watson Conversation Service', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-ii', '--common_intents', help='directory with intent csv files to be processed (all of them will be included in output json)', action='append') #-gi is functionsally equivalent to -ii
    parser.add_argument('-gi', '--common_generated_intents', help='directory with generated intent csv files to be processed (all of them will be included in output json)', action='append')
    parser.add_argument('-od', '--common_outputs_directory', required=False, help='directory where the otputs will be stored (outputs is default)')
    parser.add_argument('-oi', '--common_outputs_intents', help='file with output json with all the intents')
    parser.add_argument('-ni', '--common_intents_nameCheck', action='append', nargs=2, help="regex and replacement for intent name check, e.g. '-' '_' for to replace hyphens for underscores or '$special' '\\L' for lowercase")
    parser.add_argument('-s', '--soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)
        
    config = Cfg(args)

    NAME_POLICY = 'soft' if args.soft else 'hard'
    logger.info('STARTING: ' + os.path.basename(__file__))

    if not hasattr(config, 'common_intents'):
        logger.info('intents parameter is not defined.')
    if not hasattr(config, 'common_generated_intents'):
        logger.info('generated_intents parameter is not defined, ignoring')
    if not hasattr(config, 'common_outputs_intents'):
        logger.info('Outputs_intents parameter is not defined, output will be generated to console.')

    intents = []

    pathList = getattr(config, 'common_intents')
    if hasattr(config, 'common_generated_intents'):
        pathList = pathList + getattr(config, 'common_generated_intents')

    filesAtPath = getFilesAtPath(pathList)
    for intentFileName in sorted(filesAtPath):
        intentName = toIntentName(NAME_POLICY, args.common_intents_nameCheck, os.path.splitext(os.path.basename(intentFileName))[0])
        with openFile(intentFileName, 'r', encoding='utf8') as intentFile:
            intent = {}
            intent['intent'] = intentName
            examples = []
            for line in intentFile:
                # remove comments
                line = line.split('#')[0]
                line = line.rstrip().lower()
                #non-ascii characters fix
                #line = line.encode('utf-8')
                if line:
                    example = processExample(line, intentName, examples)
                    #adding to the list
                    if example:
                        examples.append(example)

            intent['examples'] = examples
            intents.append(intent)

    if hasattr(config, 'common_outputs_directory') and hasattr(config, 'common_outputs_intents'):
        if not os.path.exists(getattr(config, 'common_outputs_directory')):
            os.makedirs(getattr(config, 'common_outputs_directory'))
            logger.info('Created new output directory ' + getattr(config, 'common_outputs_directory'))
        with codecs.open(os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_intents')), 'w', encoding='utf8') as outputFile:
            outputFile.write(json.dumps(intents, indent=4, ensure_ascii=False))
    else:
        print(json.dumps(intents, indent=4, ensure_ascii=False))

    logger.info('FINISHING: ' + os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])
