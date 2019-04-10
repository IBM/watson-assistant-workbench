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

import json,sys,argparse, os
import lxml.etree as LET
from wawCommons import setLoggerConfig, getScriptLogger,  toCode, openFile
import logging


logger = getScriptLogger(__file__)

def main(argv):
    parser = argparse.ArgumentParser(description='Replaces sentences in text tags with codes and creates resource file with translations from codes to sentences.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('dialog', help='dialog nodes in xml format.')
    parser.add_argument('resource', help='file with generated translations from codes to sentences (JSON format - https://console-regional.stage1.ng.bluemix.net/docs/services/GlobalizationPipeline/bundles.html#globalizationpipeline_workingwithbundles)')
    # optional arguments
    parser.add_argument('-o', '--output', required=False, help='dialog nodes in xml format with all texts replaced by codes.')
    parser.add_argument('-p', '--prefix', required=False, default='TXT', help='the prefix for generated codes (alphanumeric upercase only).')
    parser.add_argument('-t', '--tagsXPath', required=False, nargs='+', default = ['//text[not(values)]', '//values'], help='XPath of tags whose text should be replaced by code.')
    parser.add_argument('-a', '--append', required=False, help='append translations to the existing resource file as new ones. (Duplicate codes will be overwritten by new ones.)', action='store_true')
    parser.add_argument('-j', '--join', required=False, help='use translations from the existing resource file and append new ones.', action='store_true')
    parser.add_argument('-i', '--inplace', required=False, help='replace input dialog by output.', action='store_true')
    parser.add_argument('-s', '--soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)
    
    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    NAME_POLICY = 'soft' if args.soft else 'hard'
    PREFIX = toCode(NAME_POLICY, args.prefix)

    # load dialog from XML
    # TODO might need UTF-8
    dialogsXML = LET.parse(args.dialog)

    # find all tags with texts to replace
    tagsToReplace = []
    for tagXPath in args.tagsXPath:
        tagsToReplace.extend(dialogsXML.xpath(tagXPath))

    # LOAD EXISTING RESOURCE FILE (TRANSLATIONS)
    if args.join:
        with openFile(args.resource, 'r') as resourceFile:
            translations = json.load(resourceFile)
    else:
        translations = {}

    counter = 0

    # REPLACE ALL TEXTS WITH CODES
    for tagToReplace in tagsToReplace:
        text = tagToReplace.text
        logger.verbose("%s: %s", tagToReplace.tag, tagToReplace.text)
        # if this tag text is not in translations dictionary (it has not a code),
        # create new code for it and add it to dictionary
        if not text in translations.values():
            translations[toCode(NAME_POLICY, PREFIX + str(counter))] = text
            counter += 1
        # replace tag text by its code
        code = translations.keys()[translations.values().index(text)] # returns key (code) for this value (text)
        tagToReplace.text = '%%' + code
        logger.verbose("-> encoded as %s", code)

    # OUTPUT NEW DIALOG
    if args.output is not None:
        with openFile(args.output, 'w') as outputFile:
            outputFile.write(LET.tostring(dialogsXML, pretty_print=True, encoding='utf8'))
    elif args.inplace:
        with openFile(args.dialog, 'w') as outputFile:
            outputFile.write(LET.tostring(dialogsXML, pretty_print=True, encoding='utf8'))
    else:
        sys.stdout.write(LET.tostring(dialogsXML, pretty_print=True, encoding='utf8'))

    # EXTEND RESOURCE FILE
    if args.append:
        with openFile(args.resource, 'r') as resourceFile:
            resourceJSON = json.load(resourceFile)
            resourceJSON.update(translations) # add new translations to existing ones (Duplicate codes will be overwritten by new ones.)
            translations = resourceJSON

    # CREATE RESOURCE FILE
    with openFile(args.resource, 'w') as resourceFile:
        resourceFile.write(json.dumps(translations, indent=4, ensure_ascii=False))

    logger.verbose('Texts were successfully replaced with codes.')

if __name__ == '__main__':
    main(sys.argv[1:])