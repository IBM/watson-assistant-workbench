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

import json, sys, argparse, os, glob, codecs
from wawCommons import printf, eprintf, getFilesAtPath, toIntentName
from cfgCommons import Cfg

if __name__ == '__main__':
    printf('\nSTARTING: ' + os.path.basename(__file__) + '\n')
    parser = argparse.ArgumentParser(description='Converts intent csv files to .json format of Watson Conversation Service', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-ii', '--common_intents', help='directory with intent csv files to be processed (all of them will be included in output json)', action='append') #-gi is functionsally equivalent to -ii
    parser.add_argument('-gi', '--common_generated_intents', help='directory with generated intent csv files to be processed (all of them will be included in output json)', action='append')
    parser.add_argument('-od', '--common_outputs_directory', required=False, help='directory where the otputs will be stored (outputs is default)')
    parser.add_argument('-oi', '--common_outputs_intents', help='file with output json with all the intents')
    parser.add_argument('-ni', '--common_intents_nameCheck', action='append', nargs=2, help="regex and replacement for intent name check, e.g. '-' '_' for to replace hyphens for underscores or '$special' '\L' for lowercase")
    parser.add_argument('-s', '--soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    parser.add_argument('-v','--common_verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    config = Cfg(args);

    VERBOSE = hasattr(config, 'common_verbose')
    NAME_POLICY = 'soft' if args.soft else 'hard'

    if not hasattr(config, 'common_intents'):
        print('intents parameter is not defined.')
    if not hasattr(config, 'common_generated_intents'):
        print('generated_intents parameter is not defined, ignoring')
    if not hasattr(config, 'common_outputs_intents'):
        print('Outputs_intents parameter is not defined, output will be generated to console.')

    intents = []

    pathList = getattr(config, 'common_intents')
    if hasattr(config, 'common_generated_intents'):
        pathList = pathList + getattr(config, 'common_generated_intents')

    filesAtPath = getFilesAtPath(pathList)
    for intentFileName in sorted(filesAtPath):
        intentName = toIntentName(NAME_POLICY, args.common_intents_nameCheck, os.path.splitext(os.path.basename(intentFileName))[0])
        with codecs.open(intentFileName, 'r', encoding='utf8') as intentFile:
            intent = {}
            intent['intent'] = intentName
            examples = []
            for line in intentFile:
                # remove comments
                line = line.split('#')[0]
                line = line.rstrip().lower()
                if line and not line in examples:
                    examples.append(line)
                elif line in examples:
                    printf('Example used twice for the intent %s, omitting:%s /n', intentName, line )
            intent['examples'] = [{'text':i} for i in examples]
            intents.append(intent)


    if hasattr(config, 'common_outputs_directory') and hasattr(config, 'common_outputs_intents'):
        if not os.path.exists(getattr(config, 'common_outputs_directory')):
            os.makedirs(getattr(config, 'common_outputs_directory'))
            printf('Created new output directory ' + getattr(config, 'common_outputs_directory'))
        with codecs.open(os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_intents')), 'w', encoding='utf8') as outputFile:
            outputFile.write(json.dumps(intents, indent=4, ensure_ascii=False, encoding='utf8'))
    else:
        print(json.dumps(intents, indent=4, ensure_ascii=False, encoding='utf8'))

    printf('\nFINISHING: ' + os.path.basename(__file__) + '\n')
