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

import json,sys,argparse, re, os
import lxml.etree as LET
from wawCommons import setLoggerConfig, getScriptLogger,  toCode, openFile
import logging


logger = getScriptLogger(__file__)

def main(argv):
    parser = argparse.ArgumentParser(description='Replaces codes in text tags with sentences specified in the resource file.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('dialog', help='dialog nodes in xml format.')
    parser.add_argument('resource', help='file with translations from codes to sentences (JSON format - https://console-regional.stage1.ng.bluemix.net/docs/services/GlobalizationPipeline/bundles.html#globalizationpipeline_workingwithbundles)')
    # optional arguments
    parser.add_argument('-o', '--output', required=False, help='dialog nodes in xml format with all texts replaced by codes.')
    parser.add_argument('-t', '--tagsXPath', required=False, nargs='+', default = ['//text[not(values)]', '//values'], help='Additional XPath of tags whose code should be replaced by text.')
    parser.add_argument('-i', '--inplace', required=False, help='replace input dialog by output.', action='store_true')
    parser.add_argument('-s', '--soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    NAME_POLICY = 'soft' if args.soft else 'hard'

    # load dialog from XML
    dialogXML = LET.parse(args.dialog)

    # find all tags with codes to replace
    tagsToReplace = []
    for tagXPath in args.tagsXPath:
        tagsToReplace.extend(dialogXML.xpath(tagXPath))

    # LOAD RESOURCE FILE (TRANSLATIONS)
    with openFile(args.resource, 'r') as resourceFile:
        translations = json.load(resourceFile)

    # REPLACE ALL CODES WITH TEXTS
    for tagToReplace in tagsToReplace:
        if tagToReplace.text is None: continue
        logger.verbose("%s: code '%s'", tagToReplace.tag, tagToReplace.text)
        textParts = tagToReplace.text.split()
        for textPart in textParts:
            if not textPart.startswith('%%'): continue # it is not a code
            code = toCode(NAME_POLICY, textPart[2:])
            # if this tag code is not in translations dictionary -> error
            if not code in translations:
                logger.error("code '%s' not in resource file!", code)
            else:
                # replace code (introduced with double %% and followed by white character or by the end) with its translation
                newText = re.sub(r"%%"+code+"(?=\s|$)", translations[code], tagToReplace.text)
                tagToReplace.text = newText
        logger.verbose("-> translated as %s", tagToReplace.text)

    # OUTPUT NEW DIALOG
    if args.output is not None:
        with openFile(args.output, 'w') as outputFile:
            outputFile.write(LET.tostring(dialogXML, pretty_print=True, encoding='utf8'))
    elif args.inplace:
        with openFile(args.dialog, 'w') as outputFile:
            outputFile.write(LET.tostring(dialogXML, pretty_print=True, encoding='utf8'))
    else:
        sys.stdout.write(LET.tostring(dialogXML, pretty_print=True, encoding='utf8'))

    logger.verbose('Codes were successfully replaced with texts.')

if __name__ == '__main__':
    main(sys.argv[1:])