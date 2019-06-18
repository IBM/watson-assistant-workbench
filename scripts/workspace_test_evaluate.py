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

import argparse
import datetime
import json
import logging
import os
import re
import sys
import time

import lxml.etree as LET

from wawCommons import getScriptLogger, openFile, setLoggerConfig

logger = getScriptLogger(__file__)

def areSame(expectedOutputJson, receivedOutputJson, failureData, parentPath):

    logger.info("ARE SAME: %s and %s", expectedOutputJson, receivedOutputJson)

    if isinstance(expectedOutputJson, str):
        if not isinstance(receivedOutputJson, str):
            failureData['message'] = 'Received output differs in type from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "Element of the type string (" + expectedOutputJson + ")"
            failureData['receivedElement'] = "Element of the type " + receivedOutputJson.__class__.__name__
            logger.info("Different type: %s and %s", expectedOutputJson, receivedOutputJson)
            return False
        if expectedOutputJson != receivedOutputJson:
            failureData['message'] = 'Received output differs from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = expectedOutputJson
            failureData['receivedElement'] = receivedOutputJson
            logger.info("NOT SAME: %s and %s", expectedOutputJson, receivedOutputJson)
            return False
        else:
            logger.info('SAME: string %s and %s are same', expectedOutputJson, receivedOutputJson)
            return True

    elif isinstance(expectedOutputJson, int):
        if not isinstance(receivedOutputJson, int):
            failureData['message'] = 'Received output differs in type from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "Element of the type int (" + str(expectedOutputJson) + ")"
            failureData['receivedElement'] = "Element of the type " + receivedOutputJson.__class__.__name__
            logger.info("Different type: %s and %s", expectedOutputJson, receivedOutputJson)
            return False
        if expectedOutputJson != receivedOutputJson:
            failureData['message'] = 'Received output differs from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = str(expectedOutputJson)
            failureData['receivedElement'] = str(receivedOutputJson)
            logger.info("NOT SAME: %s and %s", expectedOutputJson, receivedOutputJson)
            return False
        else:
            logger.info('SAME: int %s and %s are same', expectedOutputJson, receivedOutputJson)
            return True

    elif isinstance(expectedOutputJson, list):
        if not isinstance(receivedOutputJson, list):
            failureData['message'] = 'Received output differs in type from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "Element of the type list"
            failureData['receivedElement'] = "Element of the type " + receivedOutputJson.__class__.__name__
            logger.info("Different type: %s and %s", expectedOutputJson, receivedOutputJson)
            return False
        if len(expectedOutputJson) != len(receivedOutputJson):
            failureData['message'] = 'List in received output differs in length from list in expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "List of the length " + str(len(expectedOutputJson))
            failureData['receivedElement'] = "List of the length " + str(len(receivedOutputJson))
            logger.error('Different list length!')
            logger.error('expected %s', expectedOutputJson)
            logger.error('received %s', receivedOutputJson)
            return False
        else:
            for i in range(len(expectedOutputJson)):
                logger.info("STEP: Item %d", i)
                if not areSame(expectedOutputJson[i], receivedOutputJson[i], failureData, parentPath + " - " + str(i) + "th item in list"):
                    logger.error('Different list items in positon %d!', i)
                    return False
            return True

    elif isinstance(expectedOutputJson, dict):
        if not isinstance(receivedOutputJson, dict):
            failureData['message'] = 'Received output differs in type from expected output.' + " (" + parentPath + ")"
            failureData['expectedElement'] = "Element of the type dict"
            failureData['receivedElement'] = "Element of the type " + receivedOutputJson.__class__.__name__
            logger.info("Different type: %s and %s", expectedOutputJson, receivedOutputJson)
            return False
        for elementKey in expectedOutputJson:
            logger.info("STEP: Element key %s", elementKey)
            if expectedOutputJson[elementKey] is None:
                logger.info("NONE: Element with key %s is none", elementKey)
                continue
            if elementKey not in receivedOutputJson or receivedOutputJson[elementKey] is None:
                failureData['message'] = 'Received output has no key ' + elementKey + '.' + " (" + parentPath + ")"
                failureData['expectedElement'] = "Dict with key " + elementKey
                failureData['receivedElement'] = "None"
                logger.error('Missing key in received json!')
                return False
            else:
                if not areSame(expectedOutputJson[elementKey], receivedOutputJson[elementKey], failureData, parentPath + " - " + elementKey):
                    logger.error('Different dict items for key %s!', elementKey)
                    return False
        return True

    else:
        logger.error('Unsupported type of element %s, type %s!', str(expectedOutputJson), expectedOutputJson.__class__.__name__)
        return False

def createLineFailureXML(failureData):
    lineFailureXml = LET.Element('failure')
    lineFailureXml.attrib['message'] = failureData['message']
    # expected element
    lineFailureExpectedXml = LET.Element('expected')
    lineFailureXml.append(lineFailureExpectedXml)
    lineFailureExpectedXml.text = failureData['expectedElement']
    # received element
    lineFailureReceivedXml = LET.Element('received')
    lineFailureXml.append(lineFailureReceivedXml)
    lineFailureReceivedXml.text = failureData['receivedElement']
    return lineFailureXml

def main(argv):
    parser = argparse.ArgumentParser(description='Compares all dialog flows from given files and generate xml report', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('expectedFileName', help='file with expected JSONs (One at each line at key \'output_message\')')
    parser.add_argument('receivedFileName', help='file with received JSONs')
    # optional arguments
    parser.add_argument('-o','--output', required=False, help='name of generated xml file', default='test.junit.xml')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    parser.add_argument('-e','--exception_if_fail', required=False, help='script throws exception if any test fails', action='store_true')
    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    testName = re.sub(r"\.[^\.]*$", "", os.path.basename(args.expectedFileName))

    # expected JSON
    with openFile(args.expectedFileName, "r") as expectedJsonFile:
        # received JSON
        with openFile(args.receivedFileName, "r") as receivedJsonFile:

            # init whole test
            nTests = 0
            nTestsFailed = 0
            nDialogs = 0
            nDialogsFailed = 0
            firstFailedLine = None
            timeStart = time.time() # TODO: It does not make sense to measure time of the evaluation, it should be time of the testing (calling WA) instead

            # XML (whole test)
            outputXml = LET.Element('testsuites')

            # print (whole test)
            logger.info('--------------------------------------------------------------------------------')
            logger.info('-- TEST: ' + testName)
            logger.info('--------------------------------------------------------------------------------')

            # XML (new dialouge)
            dialogXml = LET.Element('testsuite')
            outputXml.append(dialogXml)

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
                    logger.error('Missing output JSON in file %s, line %d', args.receivedFileName, line)
                    sys.exit(1)
                expectedData = json.loads(expectedJsonLine)
                expectedJson = expectedData['output_message']
                receivedJson = json.loads(receivedJsonLine)

                if (dialogId == 0 or dialogId != expectedData['dialog_id']):

                    if nDialogs > 0:
                        # end previous dialog
                        logger.info('--------------------------------------------------------------------------------')
                        if nFailuresInDialog: # at least one failure in this dialog
                            logger.info('-- TEST RESULT: FAILED, TOTAL FAILURES: %d, LINE OF THE FIRST FAILURE: %d', nFailuresInDialog, firstFailedLine)
                            nDialogsFailed += 1
                        else:
                            logger.info('-- TEST RESULT: OK')
                        logger.info('--------------------------------------------------------------------------------')

                        # XML previous dialog
                        dialogXml.attrib['name'] = 'dialog ' + str(dialogId)
                        dialogXml.attrib['tests'] = str(nTestsinDialog)
                        dialogXml.attrib['failures'] = str(nFailuresInDialog)
                        dialogXml.attrib['time'] = str(time.time() - timeDialogStart)

                        # XML (new dialouge)
                        dialogXml = LET.Element('testsuite')
                        outputXml.append(dialogXml)

                    # init new dialog
                    nDialogs += 1
                    nTestsinDialog = 0
                    nFailuresInDialog = 0
                    timeDialogStart = time.time()
                    dialogId = expectedData['dialog_id']

                nTests += 1
                nTestsinDialog += 1
                timeLineStart = time.time()
                checkMessagesTime = 0
                failureData = {'expectedElement': "", 'receivedElement': ""}

                # XML
                lineXml = LET.Element('testcase')
                dialogXml.append(lineXml)
                lineXml.attrib['classname'] = 'dialog.' + str(dialogId)
                lineXml.attrib['name'] = 'line ' + str(line)
                lineXml.attrib['time'] = str(time.time() - timeLineStart)

                if not areSame(expectedJson, receivedJson, failureData, "root"):
                    # line failure
                    lineXml.append(createLineFailureXML(failureData))

                    nTestsFailed += 1
                    nFailuresInDialog += 1 # in this file
                    if firstFailedLine is None:
                        firstFailedLine = line

                    logger.info('EXPECTED OUTPUT: ' + json.dumps(expectedJson, indent=4, ensure_ascii=False))
                    logger.info('RECEIVED OUTPUT: ' + json.dumps(receivedJson, indent=4, ensure_ascii=False))
                    resultText = 'FAILED'

                else:
                    resultText = 'OK'

                logger.info('  LINE: %d, RESULT: %s, TIME: %.2f sec', line, resultText, checkMessagesTime)

                expectedJsonLine = expectedJsonFile.readline()
                receivedJsonLine = receivedJsonFile.readline()

            # end for each line
            # end previous dialog
            logger.info('--------------------------------------------------------------------------------')
            if nFailuresInDialog: # at least one failure in this dialog
                logger.info('-- TEST RESULT: FAILED, TOTAL FAILURES: %d, LINE OF THE FIRST FAILURE: %d', nFailuresInDialog, firstFailedLine)
                nDialogsFailed += 1
            else:
                logger.info('-- TEST RESULT: OK')
            logger.info('--------------------------------------------------------------------------------')

            # XML previous dialog
            dialogXml.attrib['name'] = 'dialog ' + str(dialogId)
            dialogXml.attrib['tests'] = str(nTestsinDialog)
            dialogXml.attrib['failures'] = str(nFailuresInDialog)
            dialogXml.attrib['time'] = str(time.time() - timeDialogStart)

            if receivedJsonLine: logger.error('More than expected lines in file %s, line %d', args.receivedFileName, line)

        # close files

    logger.info('-------------------------------------------------------------------------------')
    logger.info('--------------------------------------------------------------------------------')
    if nDialogsFailed: logger.info('-- SUMMARY - DIALOUGES: %s, RESULT: FAILED, FAILED DIALOGS: %d', nDialogs, nDialogsFailed)
    else: logger.info('-- SUMMARY - DIALOUGES: %s, RESULT: OK', nDialogs)
    logger.info('--------------------------------------------------------------------------------')

    outputXml.attrib['name'] = testName
    outputXml.attrib['tests'] = str(nTests)
    outputXml.attrib['failures'] = str(nTestsFailed)
    outputXml.attrib['timestamp'] = '{0:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now())
    outputXml.attrib['time'] = str(time.time() - timeStart)

    with openFile(args.output, "w") as outputFile:
        outputFile.write(LET.tostring(outputXml, pretty_print=True, encoding='unicode'))

    #as last step of our script, we raise an exception in case user required such behavior and any test failure was detected
    if args.exception_if_fail and nDialogsFailed:
        raise NameError('FailedTestDetected')

if __name__ == '__main__':
    main(sys.argv[1:])
