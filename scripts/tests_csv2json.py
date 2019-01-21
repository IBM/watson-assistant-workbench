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

import json,sys,argparse,os

from cfgCommons import Cfg
from wawCommons import printf, eprintf, toEntityName, getFilesAtPath

if __name__ == '__main__':
    printf('\nSTARTING: ' + os.path.basename(__file__) + '\n')
    parser = argparse.ArgumentParser(description='Converts tests tsv files to .json.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration fil, the optional name of file where configuration is stored.')
    parser.add_argument('-it', '--common_tests', help='directory with test tsv files to be processed (all of them will be included in output json)', action='append') #-ge is functionsally equivalent to -ie
    parser.add_argument('-gt', '--common_generated_tests', help='directory with generated test tsv files to be processed (all of them will be included in output json)', action='append')
    parser.add_argument('-od', '--common_outputs_directory', required=False, help='directory where the otputs will be stored (outputs is default)')
    parser.add_argument('-ot', '--common_outputs_tests', help='file with output json with all the tests')
    parser.add_argument('-ne', '--common_entities_nameCheck', action='append', nargs=2, help="regex and replacement for entity name check, e.g. '-' '_' for to replace hyphens for underscores or '$special' '\L' for lowercase")
    parser.add_argument('-v','--common_verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('-s', '--common_soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    args = parser.parse_args(sys.argv[1:])
    config = Cfg(args);
    VERBOSE = hasattr(config, 'common_verbose')

    if args.common_soft: NAME_POLICY = 'soft'
    else: NAME_POLICY = 'hard'
    NAME_POLICY = 'soft'

    if not hasattr(config, 'common_tests'):
        print('tests parameter is not defined.')
        exit(1)
    if not hasattr(config, 'common_generated_tests'):
        print('generated_tests parameter is not defined, ignoring')
    if not hasattr(config, 'common_outputs_tests'):
        print('Outputs_tests parameter is not defined, output will be generated to console.')

    pathList = getattr(config, 'common_tests')
    if hasattr(config, 'common_generated_tests'):
        pathList = pathList + getattr(config, 'common_generated_tests')

    dialogId = 1
    outputString = ""
    filesAtPath = getFilesAtPath(pathList)
    for testFileName in filesAtPath:
        testName = toEntityName(NAME_POLICY, getattr(config, 'common_entities_nameCheck') if hasattr(config, 'common_entities_nameCheck') else None, os.path.splitext(os.path.basename(testFileName))[0])
        testName = os.path.splitext(os.path.basename(testFileName))[0]

#                testName = os.path.splitext(testFileName)[0].lower()
        with open(testFileName, "r") as entityFile:

            for line in entityFile.readlines():
                # remove comments
                line = line.split('#')[0]
                line = line.strip()
                if line:
                    if line == '===': # new dialog
                        dialogId += 1
                    else:
                        # create new test
                        testJSON = {}
                        testJSON['dialog_id'] = dialogId

                        testMessages = line.split('\t')
                        testJSON['input_message'] = {}
                        testJSON['input_message']['input'] = {}
                        testJSON['input_message']['input']['text'] = testMessages[0]
                        testJSON['output_message'] = {}
                        testJSON['output_message']['output'] = {}
                        testJSON['output_message']['output']['text'] = []
                        testJSON['output_message']['output']['text'].append(testMessages[1])
                        outputString += json.dumps(testJSON).encode('utf8') + "\n"

    if getattr(config, 'common_outputs_directory') and hasattr(config, 'common_outputs_tests'):
        if not os.path.exists(getattr(config, 'common_outputs_directory')):
            os.makedirs(getattr(config, 'common_outputs_directory'))
            print('Created new output directory ' + getattr(config, 'common_outputs_tests'))
        with open(os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_tests')), 'w') as outputFile:
            outputFile.write(outputString)
        if VERBOSE: printf("Entities json '%s' was successfully created\n", os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_tests')))
    else:
        print outputString
        if VERBOSE: printf("Entities json was successfully created\n", os.path.basename(__file__))

    printf('\nFINISHING: ' + os.path.basename(__file__) + '\n')
