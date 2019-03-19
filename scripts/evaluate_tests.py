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

import json, sys, argparse, requests, os, time, datetime, re
import lxml.etree as LET
from wawCommons import printf, eprintf

try:
    basestring            # Python 2
except NameError:
    basestring = (str, )  # Python 3


def areSame(expectedOutputJson, receivedOutputJson, failureData, parentPath):

    printf("ARE SAME: %s and %s\n", expectedOutputJson, receivedOutputJson)

    if isinstance(expectedOutputJson, basestring):
        if not isinstance(receivedOutputJson, basestring):
            failureData['message'] = 'Received output differs in type from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "Element of the type string (" + expectedOutputJson + ")"
            failureData['receivedElement'] = "Element of the type " + receivedOutputJson.__class__.__name__
            printf("Different type: %s and %s\n", expectedOutputJson, receivedOutputJson)
            return False
        if expectedOutputJson != receivedOutputJson:
            failureData['message'] = 'Received output differs from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = expectedOutputJson
            failureData['receivedElement'] = receivedOutputJson
            printf("NOT SAME: %s and %s\n", expectedOutputJson, receivedOutputJson)
            return False
        else:
            printf('SAME: basestring %s and %s are same\n', expectedOutputJson, receivedOutputJson)
            return True

    if isinstance(expectedOutputJson, int):
        if not isinstance(receivedOutputJson, int):
            failureData['message'] = 'Received output differs in type from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "Element of the type int (" + str(expectedOutputJson) + ")"
            failureData['receivedElement'] = "Element of the type " + receivedOutputJson.__class__.__name__
            printf("Different type: %s and %s\n", expectedOutputJson, receivedOutputJson)
            return False
        if expectedOutputJson != receivedOutputJson:
            failureData['message'] = 'Received output differs from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = str(expectedOutputJson)
            failureData['receivedElement'] = str(receivedOutputJson)
            printf("NOT SAME: %s and %s\n", expectedOutputJson, receivedOutputJson)
            return False
        else:
            printf('SAME: int %s and %s are same\n', expectedOutputJson, receivedOutputJson)
            return True

    elif isinstance(expectedOutputJson, list):
        if not isinstance(receivedOutputJson, list):
            failureData['message'] = 'Received output differs in type from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "Element of the type list"
            failureData['receivedElement'] = "Element of the type " + receivedOutputJson.__class__.__name__
            printf("Different type: %s and %s\n", expectedOutputJson, receivedOutputJson)
            return False
        if len(expectedOutputJson) != len(receivedOutputJson):
            failureData['message'] = 'List in received output differs in length from list in expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "List of the length " + str(len(expectedOutputJson))
            failureData['receivedElement'] = "List of the length " + str(len(receivedOutputJson))
            printf('ERROR: Different list length!\n')
            printf('expected %s\n', expectedOutputJson)
            printf('received %s\n', receivedOutputJson)
            return False
        else:
            for i in range(len(expectedOutputJson)):
                printf("STEP: Item %d\n", i)
                if not areSame(expectedOutputJson[i], receivedOutputJson[i], failureData, parentPath + " - " + str(i) + "th item in list"):
                    printf('ERROR: Different list items in positon %d!\n', i)
                    return False
            return True

    elif isinstance(expectedOutputJson, dict):
        if not isinstance(receivedOutputJson, dict):
            failureData['message'] = 'Received output differs in type from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "Element of the type dict"
            failureData['receivedElement'] = "Element of the type " + receivedOutputJson.__class__.__name__
            printf("Different type: %s and %s\n", expectedOutputJson, receivedOutputJson)
            return False
        for elementKey in expectedOutputJson:
            printf("STEP: Element key %s\n", elementKey)
            if expectedOutputJson[elementKey] is None:
                printf("NONE: Element with key %s is none\n", elementKey)
                continue
            if elementKey not in receivedOutputJson or receivedOutputJson[elementKey] is None:
                failureData['message'] = 'Received output has no key ' + elementKey + '.' + " (" + parentPath + ")"
                failureData['expectedElement'] = "Dict with key " + elementKey
                failureData['receivedElement'] = "None"
                printf('ERROR: Missing key in received json!\n')
                return False
            else:
                if not areSame(expectedOutputJson[elementKey], receivedOutputJson[elementKey], failureData, parentPath + " - " + elementKey):
                    printf('ERROR: Different dict items for key %s!\n', elementKey)
                    return False
        return True

    else:
        eprintf('ERROR: Unsupported type of element %s, type %s!\n', str(expectedOutputJson), expectedOutputJson.__class__.__name__)
        return False

def createLineFailureXML(failureData):
    lineFailureXml = LET.Element('failure')
    lineFailureXml.attrib['message'] = failureData['message']
    # expected element
    lineFailureExpectedXml = LET.Element('expected')
    lineFailureExpectedXml.text = failureData['expectedElement']
    lineFailureXml.append(lineFailureExpectedXml)
    # received element
    lineFailureReceivedXml = LET.Element('received')
    lineFailureReceivedXml.text = failureData['receivedElement']
    lineFailureXml.append(lineFailureReceivedXml)
    return lineFailureXml

def main(argv):
    parser = argparse.ArgumentParser(description='Compares all dialog flows from given files and generate xml report', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('expectedFileName', help='file with expected JSONs (One at each line at key \'output_message\')')
    parser.add_argument('receivedFileName', help='file with received JSONs')
    # optional arguments
    parser.add_argument('-o','--output', required=False, help='name of generated xml file', default='test.junit.xml')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(argv)

    VERBOSE = args.verbose

    testName = re.sub(r"\.[^\.]*$", "", os.path.basename(args.expectedFileName))

    # expected JSON
    with open(args.expectedFileName, "r") as expectedJsonFile:
        # received JSON
        with open(args.receivedFileName, "r") as receivedJsonFile:

            # init whole test
            nDialogs = 0
            nDialogsFailed = 0
            firstFailedLine = None
            timeStart = time.time()

            # XML (whole test)
            outputXml = LET.Element('testsuites')

            # print (whole test)
            printf('--------------------------------------------------------------------------------\n')
            printf('-- TEST: ' + testName + '\n')
            printf('--------------------------------------------------------------------------------\n')

            # XML (new dialouge)
            dialogXml = LET.Element('testsuite')

            expectedJsonLine = expectedJsonFile.readline()
            receivedJsonLine = receivedJsonFile.readline()

            line = 0
            dialogId = 0
            nTestsinDialog = 0
            nFailuresInDialog = 0
            timeDialogStart = time.time()

            # for every line
            while expectedJsonLine:
                line += 1
                if not receivedJsonLine: # no more received line
                    eprintf('ERROR: Missing output JSON in file %s, line %d', args.receivedFileName, line)
                    sys.exit(1)
                expectedData = json.loads(expectedJsonLine)
                expectedJson = expectedData['output_message']
                receivedJson = json.loads(receivedJsonLine)

                if (dialogId == 0 or dialogId != expectedData['dialog_id']):

                    if nDialogs > 0:
                        # end previous dialog
                        printf('--------------------------------------------------------------------------------\n')
                        if nFailuresInDialog: # at least one failure in this dialog
                            printf('-- TEST RESULT: FAILED, TOTAL FAILURES: %d, LINE OF THE FIRST FAILURE: %d\n', nFailuresInDialog, firstFailedLine)
                            nDialogsFailed += 1
                        else:
                            printf('-- TEST RESULT: OK\n')
                        printf('--------------------------------------------------------------------------------\n')

                        # XML previous dialog
                        dialogXml.attrib['name'] = 'dialog ' + str(dialogId)
                        dialogXml.attrib['tests'] = str(nTestsinDialog)
                        dialogXml.attrib['failures'] = str(nFailuresInDialog)
                        dialogXml.attrib['time'] = str(time.time() - timeDialogStart)
                        outputXml.append(dialogXml)

                    # init new dialog
                    nDialogs += 1
                    nTestsinDialog = 0
                    nFailuresInDialog = 0
                    timeDialogStart = time.time()
                    dialogId = expectedData['dialog_id']

                    # XML (new dialouge)
                    dialogXml = LET.Element('testsuite')

                nTestsinDialog += 1
                timeLineStart = time.time()
                checkMessagesTime = 0
                failureData = {'expectedElement': "", 'receivedElement': ""}

                # XML
                lineXml = LET.Element('testcase')
                lineXml.attrib['name'] = 'line ' + str(line)
                lineXml.attrib['time'] = str(time.time() - timeLineStart)
                dialogXml.append(lineXml)

                if not areSame(expectedJson, receivedJson, failureData, "root"):
                    # line failure
                    lineXml.append(createLineFailureXML(failureData))

                    nFailuresInDialog += 1 # in this file
                    if firstFailedLine is None:
                        firstFailedLine = line

                    printf('EXPECTED OUTPUT: ' + json.dumps(expectedJson, indent=4, ensure_ascii=False).encode('utf8') + '\n')
                    printf('RECEIVED OUTPUT: ' + json.dumps(receivedJson, indent=4, ensure_ascii=False).encode('utf8') + '\n')
                    resultText = 'FAILED'

                else:
                    resultText = 'OK'

                printf('  LINE: %d, RESULT: %s, TIME: %.2f sec\n', line, resultText, checkMessagesTime)

                expectedJsonLine = expectedJsonFile.readline()
                receivedJsonLine = receivedJsonFile.readline()

            # end for each line

            if receivedJsonLine: eprintf('ERROR: More than expected lines in file %s, line %d', args.receivedFileName, line)

        # close files

    printf('\n--------------------------------------------------------------------------------\n')
    printf('--------------------------------------------------------------------------------\n')
    if nDialogsFailed: printf('-- SUMMARY - DIALOUGES: %s, RESULT: FAILED, FAILED DIALOGS: %d\n', nDialogs, nDialogsFailed)
    else: printf('-- SUMMARY - DIALOUGES: %s, RESULT: OK\n', nDialogs)
    printf('--------------------------------------------------------------------------------\n')

    outputXml.attrib['name'] = testName
    outputXml.attrib['tests'] = str(nDialogs)
    outputXml.attrib['failures'] = str(nDialogsFailed)
    outputXml.attrib['timestamp'] = '{0:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now())
    outputXml.attrib['time'] = str(time.time() - timeStart)

    with open(args.output, "w") as outputFile:
        outputFile.write(LET.tostring(outputXml, pretty_print=True, encoding='utf8'))

if __name__ == '__main__':
    main(sys.argv[1:])

