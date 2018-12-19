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

import json, sys, argparse, os
import lxml.etree as LET
from wawCommons import printf, eprintf

try:
    basestring            # Python 2
except NameError:
    basestring = (str, )  # Python 3


def convertDialog(dialogNodesJSON):
    dialogXML = LET.Element("nodes")
    #print dialogNodesJSON
    # find root
    rootJSON = findNode(dialogNodesJSON, None, None)
    expandNode(dialogNodesJSON, dialogXML, rootJSON)
    if (len(dialogNodesJSON) > 0):
        sys.stderr.write("There are " + str(len(dialogNodesJSON)) + " unprocessed nodes: " + str(dialogNodesJSON) + "\n")
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

    #condition
    if 'conditions' in nodeJSON and nodeJSON['conditions']:
        condition = LET.Element('condition')
        condition.text = nodeJSON['conditions']
        nodeXML.append(condition)
    #context
    if 'context' in nodeJSON and nodeJSON['context']:
        convertAll(nodeXML, nodeJSON, 'context')
    #output
    if 'output' in nodeJSON and nodeJSON['output']:
        convertAll(nodeXML, nodeJSON, 'output')
        if 'text' in nodeJSON['output'] and not isinstance(nodeJSON['output']['text'], basestring):
          outputXML = nodeXML.find('output').find('text').tag = 'textValues'
        if 'generic' in nodeJSON['output']: # generic structure is always a list
            nodeXML.find('output').find('generic').find('values').attrib['structure'] = 'listItem'
    #goto
    if 'next_step' in nodeJSON and nodeJSON['next_step']:
        nodeGoToXML = LET.Element('goto')
        nodeXML.append(nodeGoToXML)
        if 'dialog_node' in nodeJSON['next_step']:
            nodeGoToTargetXML = LET.Element('target')
            nodeGoToTargetXML.text = nodeJSON['next_step']['dialog_node']
            nodeGoToXML.append(nodeGoToTargetXML)
        if 'selector' in nodeJSON['next_step']:
            nodeGoToSelectorXML = LET.Element('selector')
            nodeGoToSelectorXML.text = nodeJSON['next_step']['selector']
            nodeGoToXML.append(nodeGoToSelectorXML)
        # cant use this because target != dialog_node
        #convertAll(nodeXML, nodeJSON, 'go_to')
    if 'actions' in nodeJSON and nodeJSON['actions']:
      convertAll(nodeXML, nodeJSON, 'actions')
      actionsXML = LET.Element('actions')
      for actionXML in nodeXML.findall('actions'):
        actionXML.tag = 'action'
        actionsXML.append(actionXML)
      nodeXML.append(actionsXML)
    #TODO handlers
    #TODO slots
    #TODO responses
    return nodeXML

# upperNodeXML: where to append this tag
# nodeJSON: node, whose tag is converted
# keyJSON: name of tag to convert
def convertAll(upperNodeXML, nodeJSON, keyJSON, nameXML = None):
    if nameXML is None:
      nameXML = keyJSON
    if isinstance(nodeJSON[keyJSON], basestring):
        nodeXML = LET.Element(str(nameXML))
        nodeXML.text = nodeJSON[keyJSON]
        upperNodeXML.append(nodeXML)
    elif isinstance(nodeJSON[keyJSON], list):
        for i in range(len(nodeJSON[keyJSON])):
            listItemJSON = nodeJSON[keyJSON][i]
            convertAll(upperNodeXML, nodeJSON[keyJSON], i, keyJSON)
    elif isinstance(nodeJSON[keyJSON], dict):
        nodeXML = LET.Element(str(nameXML))
        upperNodeXML.append(nodeXML)
        for subKeyJSON in nodeJSON[keyJSON]:
            convertAll(nodeXML, nodeJSON[keyJSON], subKeyJSON)
    elif nodeJSON[keyJSON] is not None:
        # int, long, float, complex, boolean?
        nodeXML = LET.Element(str(nameXML))
        nodeXML.text = str(nodeJSON[keyJSON])
        upperNodeXML.append(nodeXML)

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decompose Bluemix conversation service dialog in .json format to dialog files in .xml format', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('dialog', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='file with dialog in .json format, if not specified, dialog is read from standard input')
    # optional arguments
    parser.add_argument('-d', '--dialogDir', required=False, help='directory with dialog files. If not specified, output is printed to standard output')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    VERBOSE = args.verbose
    STDOUT = not args.dialogDir

    # load dialogs JSON
    dialogsJSON = json.load(args.dialog)

    # convert dialogs
    dialogsXML = convertDialog(dialogsJSON)

    # return dialog XML
    if args.dialogDir:
        # print to file
        dialogFileName = os.path.join(args.dialogDir, "dialog.xml")
        with open(dialogFileName, "w") as dialogFile:
            dialogFile.write(LET.tostring(dialogsXML, pretty_print=True, encoding='utf8'))
    else:
        # print to standard output
        print(LET.tostring(dialogsXML, pretty_print=True, encoding='utf8'))
