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
import json
import logging
import os
import sys

import lxml.etree as LET

from wawCommons import getScriptLogger, openFile, setLoggerConfig

logger = getScriptLogger(__file__)

try:
    basestring            # Python 2
except NameError:
    basestring = (str, )  # Python 3


def convertDialog(dialogNodesJSON):

    dialogXML = LET.Element("nodes", nsmap=NSMAP)

    #print dialogNodesJSON
    # find root
    rootJSON = findNode(dialogNodesJSON, None, None)
    expandNode(dialogNodesJSON, dialogXML, rootJSON)
    if (len(dialogNodesJSON) > 0):
        logger.error("There are " + str(len(dialogNodesJSON)) + " unprocessed nodes: " + str(dialogNodesJSON))
    return dialogXML

# dialogNodesJSON: rest of nodes to process
# upperNodeXML: where to append siblings
# nodeJSON: node to expand
# Converts this node and recursively all its children and siblings
def expandNode(dialogNodesJSON, upperNodeXML, nodeJSON):
    nodeXML = convertNode(nodeJSON)
    upperNodeXML.append(nodeXML)

    # find first child
    childJSON = findNode(dialogNodesJSON, nodeJSON['dialog_node'], None) # expanded node as parent, None as sibling
    if childJSON is not None:
        childrenXML = LET.Element('nodes') # create 'nodes' tag
        nodeXML.append(childrenXML)
        expandNode(dialogNodesJSON, childrenXML, childJSON) # expand first child (process its siblings and children)

    # find next sibling
    siblingJSON = findNode(dialogNodesJSON, nodeJSON['parent'] if 'parent' in nodeJSON else None, nodeJSON['dialog_node'])
    if siblingJSON is not None:
        expandNode(dialogNodesJSON, upperNodeXML, siblingJSON) # expand next sibling (process its siblings and children)

def convertNode(nodeJSON):
    nodeXML = LET.Element('node')
    nodeXML.attrib['name'] = nodeJSON['dialog_node']
    logger.verbose("node '%s'", nodeXML.attrib['name'])

    #title
    if 'title' in nodeJSON:
        if nodeJSON['title'] != nodeJSON['dialog_node']: # WA adds title to all uploaded workspaces equal to dialog_name, this is cleanup TODO: remove the conditions when upgrading to new version of WA API
            nodeXML.attrib['title'] = nodeJSON['title']
    #type
    if 'type' in nodeJSON:
        typeNodeXML = LET.Element('type')
        typeNodeXML.text = nodeJSON['type']
        nodeXML.append(typeNodeXML)
    #disabled
    if 'disabled' in nodeJSON:
        disabledNodeXML = LET.Element('disabled')
        nodeXML.append(disabledNodeXML)
        disabledNodeXML.text = str(nodeJSON['disabled'])
        #disabledNodeXML.attrib['type'] = "boolean"
    #condition
    if 'conditions' in nodeJSON:
        conditionXML = LET.Element('condition')
        nodeXML.append(conditionXML)
        if nodeJSON['conditions'] is None: # null value
            conditionXML.attrib[XSI+'nil'] = "true"
        else:
            conditionXML.text = nodeJSON['conditions']
    #context
    if 'context' in nodeJSON:
        if nodeJSON['context'] is None: # null value
            contextXML = LET.Element('context')
            nodeXML.append(contextXML)
            contextXML.attrib[XSI+'nil'] = "true"
        elif not nodeJSON['context']: # not None but empty
             contextXML = LET.Element('context')
             nodeXML.append(contextXML)
             if isinstance(nodeJSON['context'], dict):
                 contextXML.attrib['structure'] = "emptyDict"
             elif isinstance(nodeJSON['context'], list):
                 contextXML.attrib['structure'] = "emptyList"
             else:
                 contextXML.text = ""
        else:
            convertAll(nodeXML, nodeJSON, 'context')
    #output
    if 'output' in nodeJSON:
        if nodeJSON['output'] is None: # null value
            outputXML = LET.Element('output')
            nodeXML.append(outputXML)
            outputXML.attrib[XSI+'nil'] = "true"
        elif not nodeJSON['output']: # not None but empty
            outputXML = LET.Element('output')
            nodeXML.append(outputXML)
            if isinstance(nodeJSON['output'], dict):
                outputXML.attrib['structure'] = "emptyDict"
            elif isinstance(nodeJSON['output'], list):
                outputXML.attrib['structure'] = "emptyList"
            else:
                outputXML.text = ""
        else:
            convertAll(nodeXML, nodeJSON, 'output')
            if 'text' in nodeJSON['output'] and not isinstance(nodeJSON['output']['text'], basestring):
              outputXML = nodeXML.find('output').find('text').tag = 'textValues'
            if 'generic' in nodeJSON['output']:
                if nodeJSON['output']['generic'] is None or len(nodeXML.find('output').findall('generic')) == 0:
                    return
                if len(nodeXML.find('output').findall('generic')) == 1 and nodeXML.find('output').find('generic').attrib['structure'] is None:
                     # generic nodes has to be of type array - set if not defined
                    nodeXML.find('output').find('generic').attrib['structure'] = 'listItem'

                # generic is not none or empty
                for genericItemXML in nodeXML.find('output').findall('generic'):
                    if genericItemXML.find('response_type') is None:
                        logger.error("'response_type' is missing in the output of the node " + nodeJSON['dialog_node'])
                    elif genericItemXML.find('response_type').text == 'text': # TODO check other response_types
                        if genericItemXML.findall('values') is not None:
                            if len(genericItemXML.findall('values')) == 1:
                                if not 'structure' in genericItemXML.find('values').attrib: # structure is not specified yet
                                    # values has to be of type array
                                    genericItemXML.find('values').attrib['structure'] = 'listItem'
                                    logger.verbose("setting 'listitem' attribute to 'values' tag")

    #goto
    if 'next_step' in nodeJSON:
        nodeGoToXML = LET.Element('goto')
        nodeXML.append(nodeGoToXML)
        if nodeJSON['next_step'] is None: # null value
            nodeGoToXML.attrib[XSI+'nil'] = "true"
        elif nodeJSON['next_step']:
            if 'behavior' in nodeJSON['next_step']:
                nodeGoToBehaviorXML = LET.Element('behavior')
                nodeGoToXML.append(nodeGoToBehaviorXML)
                if nodeJSON['next_step']['behavior'] is None:
                    nodeGoToBehaviorXML.attrib[XSI+'nil'] = "true"
                else:
                    nodeGoToBehaviorXML.text = nodeJSON['next_step']['behavior']
            if 'dialog_node' in nodeJSON['next_step']:
                nodeGoToTargetXML = LET.Element('target')
                nodeGoToXML.append(nodeGoToTargetXML)
                if nodeJSON['next_step']['dialog_node'] is None:
                    nodeGoToTargetXML.attrib[XSI+'nil'] = "true"
                else:
                    nodeGoToTargetXML.text = nodeJSON['next_step']['dialog_node']
            if 'selector' in nodeJSON['next_step']:
                nodeGoToSelectorXML = LET.Element('selector')
                nodeGoToXML.append(nodeGoToSelectorXML)
                if nodeJSON['next_step']['selector'] is None:
                    nodeGoToSelectorXML.attrib[XSI+'nil'] = "true"
                else:
                    nodeGoToSelectorXML.text = nodeJSON['next_step']['selector']
        # cant use this because target != dialog_node
        #convertAll(nodeXML, nodeJSON, 'go_to')
    #digression
    if 'digress_in' in nodeJSON:
        digressInXML = LET.Element('digress_in')
        nodeXML.append(digressInXML)
        if nodeJSON['digress_in'] is None: # null value
            digressInXML.attrib[XSI+'nil'] = "true"
        else:
            digressInXML.text = nodeJSON['digress_in']
    if 'digress_out' in nodeJSON:
        digressOutXML = LET.Element('digress_out')
        nodeXML.append(digressOutXML)
        if nodeJSON['digress_out'] is None: # null value
            digressOutXML.attrib[XSI+'nil'] = "true"
        else:
            digressOutXML.text = nodeJSON['digress_out']
    if 'digress_out_slots' in nodeJSON:
        digressOutSlotsXML = LET.Element('digress_out_slots')
        nodeXML.append(digressOutSlotsXML)
        if nodeJSON['digress_out_slots'] is None: # null value
            digressOutSlotsXML.attrib[XSI+'nil'] = "true"
        else:
            digressOutSlotsXML.text = nodeJSON['digress_out_slots']
    #metadata
    if 'metadata' in nodeJSON:
        if nodeJSON['metadata'] is None: # null value
            metadataXML = LET.Element('metadata')
            nodeXML.append(metadataXML)
            metadataXML.attrib[XSI+'nil'] = "true"
        elif not nodeJSON['metadata']: # not None but empty
            metadataXML = LET.Element('metadata')
            nodeXML.append(metadataXML)
            if isinstance(nodeJSON['metadata'], dict):
                metadataXML.attrib['structure'] = "emptyDict"
            elif isinstance(nodeJSON['metadata'], list):
                metadataXML.attrib['structure'] = "emptyList"
            else:
                metadataXML.text = ""
        else:
            convertAll(nodeXML, nodeJSON, 'metadata')
    #actions
    if 'actions' in nodeJSON and nodeJSON['actions']:
        if nodeJSON['actions'] is None: # null value
            actionsXML = LET.Element('actions')
            nodeXML.append(actionsXML)
            actionsXML.attrib[XSI+'nil'] = "true"
        elif nodeJSON['actions']: # not None but empty
            convertAll(nodeXML, nodeJSON, 'actions')
            # action -> actions - action
            actionsXML = LET.Element('actions')
            for actionXML in nodeXML.findall('actions'):
                actionXML.tag = 'action'
                actionsXML.append(actionXML)
            nodeXML.append(actionsXML)

    #TODO handlers
    #events
    if 'event_name' in nodeJSON:
        eventXML = LET.Element('event_name')
        nodeXML.append(eventXML)
        if nodeJSON['event_name'] is None: # null value
            eventXML.attrib[XSI+'nil'] = "true"
        else:
            eventXML.text = nodeJSON['event_name']
    #TODO slots
    #TODO responses

    return nodeXML

# upperNodeXML: where to append this tag
# nodeJSON: node, whose tag is converted
# keyJSON: name of tag to convert
def convertAll(upperNodeXML, nodeJSON, keyJSON, nameXML = None):

    structure = None
    if nameXML is None:
        nameXML = keyJSON
    else:
        structure = "listItem"
        logger.verbose("structure 'listItem'")
    logger.verbose("name '%s'", nameXML)

    # None
    if nodeJSON[keyJSON] is None:
        logger.verbose("node is None")
        nodeXML = LET.Element(str(nameXML))
        upperNodeXML.append(nodeXML)
        if structure is not None and nameXML != "action" and nameXML != "actions":
            nodeXML.attrib['structure'] = "listItem"
            logger.verbose("adding structure 'listItem' to node")
        nodeXML.attrib[XSI+'nil'] = "true"
    # list
    elif isinstance(nodeJSON[keyJSON], list):
        logger.verbose("node is list")
        if len(nodeJSON[keyJSON]) == 0:
            nodeXML = LET.Element(str(nameXML))
            upperNodeXML.append(nodeXML)
            nodeXML.attrib['structure'] = "emptyList"
            logger.verbose("node is 'emptyList'")
            logger.verbose("node '%s' is 'emptyList'", nodeXML.tag)

        else:
            if upperNodeXML.tag != "output" and upperNodeXML.tag != "context" and upperNodeXML.tag != "node":
                pass
#                upperNodeXML.attrib['structure'] = "listItem"
#                logger.verbose("setting listItem")
            for i in range(len(nodeJSON[keyJSON])):
                convertAll(upperNodeXML, nodeJSON[keyJSON], i, keyJSON)
    # dict
    elif isinstance(nodeJSON[keyJSON], dict):
        logger.verbose("node is dict")
        if not nodeJSON[keyJSON]: #empty dict
            nodeXML = LET.Element(str(nameXML))
            upperNodeXML.append(nodeXML)
            nodeXML.attrib['structure'] = "emptyDict"
            logger.verbose("node '%s' is 'emptyDict'", nodeXML.tag)
        else:
            nodeXML = LET.Element(str(nameXML))
            upperNodeXML.append(nodeXML)
            if structure is not None and nameXML != "action" and nameXML != "actions":
                nodeXML.attrib['structure'] = "listItem"
                logger.verbose("add structure 'listItem' for '%s'", nameXML)
            for subKeyJSON in nodeJSON[keyJSON]:
                convertAll(nodeXML, nodeJSON[keyJSON], subKeyJSON)
    # string
    elif isinstance(nodeJSON[keyJSON], basestring):
        logger.verbose("node is string")
        nodeXML = LET.Element(str(nameXML))
        upperNodeXML.append(nodeXML)
        if structure is not None and nameXML != "action" and nameXML != "actions":
            nodeXML.attrib['structure'] = "listItem"
            logger.verbose("add structure 'listItem' for '%s'", nameXML)
        nodeXML.text = nodeJSON[keyJSON]
    # bool
    elif isinstance(nodeJSON[keyJSON], bool):
        logger.verbose("node is boolean")
        nodeXML = LET.Element(str(nameXML))
        upperNodeXML.append(nodeXML)
        if structure is not None and nameXML != "action" and nameXML != "actions":
            nodeXML.attrib['structure'] = "listItem"
            logger.verbose("add structure 'listItem' for '%s'", nameXML)
        nodeXML.text = str(nodeJSON[keyJSON])
        nodeXML.attrib['type'] = "boolean"
    # int, long, float, complex
    elif isNumber(nodeJSON[keyJSON]):
        logger.verbose("node is number")
        nodeXML = LET.Element(str(nameXML))
        upperNodeXML.append(nodeXML)
        if structure is not None and nameXML != "action" and nameXML != "actions":
            nodeXML.attrib['structure'] = "listItem"
            logger.verbose("add structure 'listItem' for '%s'", nameXML)
        nodeXML.text = str(nodeJSON[keyJSON])
        nodeXML.attrib['type'] = "number"
    else:
        logger.error("Unknown value type")

# find and return node with specific parent and previous sibling
# removing it from the list
def findNode(dialogNodesJSON, parentName, siblingName):
    for nodeJSON in dialogNodesJSON:
        if getValue(nodeJSON, 'parent') == parentName and getValue(nodeJSON, 'previous_sibling') == siblingName:
            dialogNodesJSON.remove(nodeJSON)
            return nodeJSON
    return None

def getValue(dict, key):
    if key in dict:
        # check another null like values
        return dict[key]
    else:
        return None

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def main(argv):
    parser = argparse.ArgumentParser(description='Decompose Bluemix conversation service dialog in .json format to dialog files in .xml format', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('dialog', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='file with dialog in .json format, if not specified, dialog is read from standard input')
    # optional arguments
    parser.add_argument('-d', '--dialogDir', required=False, help='directory with dialog files. If not specified, output is printed to standard output')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)
    
    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    global STDOUT
    STDOUT = not args.dialogDir

    # XML namespaces
    global XSI_NAMESPACE
    global XSI
    global NSMAP
    XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
    XSI = "{%s}" % XSI_NAMESPACE
    NSMAP = {"xsi" : XSI_NAMESPACE}

    # load dialogs JSON
    dialogsJSON = json.load(args.dialog, encoding='utf-8')

    # convert dialogs
    dialogsXML = convertDialog(dialogsJSON)

    # return dialog XML
    if args.dialogDir:
        # print to file
        dialogFileName = os.path.join(args.dialogDir, "dialog.xml")
        with openFile(dialogFileName, "w") as dialogFile:
            dialogFile.write(LET.tostring(dialogsXML, pretty_print=True, encoding='unicode'))
    else:
        # print to standard output
        print(LET.tostring(dialogsXML, pretty_print=True, encoding='unicode'))

if __name__ == '__main__':
    main(sys.argv[1:])
