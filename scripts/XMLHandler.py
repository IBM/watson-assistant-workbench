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

import lxml.etree as XML

from wawCommons import getScriptLogger

logger = getScriptLogger(__file__)

NAME_POLICY = 'soft'

# Watson Assistant limits number of options currently to 5, we cut the end of the list of options if it is longer
MAX_OPTIONS = 50

class XMLHandler(object):

    def __init__(self):
        pass

    def convertDialogData(self, dialogData, nodes):
        """ Converts Dialog Data of a single domain into XML and returns pointer to the root XML element. """
        nodesXml = XML.Element('nodes')
        for node_name in nodes: #for each node in the domain
            nodeData = dialogData.getNode(node_name)
            if nodeData == None:
                logger.warning("Not found a definition for a node name %s",node_name)
                continue

            # construct the XML structure for each node
            nodeXml = XML.Element('node', name=node_name)
            #Condition
            conditionXml = XML.Element('condition')
            conditionXml.text = nodeData.getCondition()
            nodeXml.append(conditionXml)
            #output
            nodeXml.append(self._createOutputElement(nodeData.getChannelOutputs(), nodeData.getButtons(), nodeData.getFoldable()))
            if nodeData.getVariables():
                nodeXml.append(self._createContextElement(nodeData.getVariables()))
            if nodeData.getJumpToTarget() and nodeData.getJumpToSelector():
                nodeXml.append(self._createGotoElement(nodeData.getJumpToTarget(), nodeData.getJumpToSelector()))
            nodesXml.append(nodeXml)
        return nodesXml

    def printXml(self, xmlDocument, prettyPrint=True):
        """ Converts xmlDocument to string. """
        if prettyPrint:
            return XML.tostring(xmlDocument, pretty_print=prettyPrint, encoding='unicode')
        else:
            return XML.tostring(xmlDocument, method='c14n', encoding='unicode')

    def _createOutputElement(self, channels, buttons, foldables):
        """ Converts output channels into XML structure. """
        outputXml = XML.Element('output')
        if channels:
            for channelName, channelValues in channels.items():
                if channelName == '1':
                    textValuesXml = XML.Element('textValues')
                    for item in channelValues:
                        textValuesXml.append(self._createXmlElement('values', item))
                        outputXml.append(textValuesXml)
                    continue

                output = self._concatenateOutputs(channelValues)
                if channelName == '2':
                    outputXml.append(self._createXmlElement('timeout', output))
                elif channelName == '3':
                    outputXml.append(self._createXmlElement('sound', output))
                elif channelName == '4':
                    outputXml.append(self._createXmlElement('tts', output))
                elif channelName == '5':
                    outputXml.append(self._createXmlElement('talking_head', output))
                elif channelName == '6':
                    outputXml.append(self._createXmlElement('paper_head', output))
                elif channelName == '7':
                    outputXml.append(self._createXmlElement('graphics', output))
                elif channelName == '8':
                    outputXml.append(self._createXmlElement('url', output))
                else:
                    logger.warning('Unrecognized channel: %s, value: %s', channelName, output)

        if buttons:
            #segment generating buttons to generic - we might return to it when WA format gets more stable
            '''
            genericXml = XML.Element('generic', structure = 'listItem')
            genericXml.append(self._createXmlElement('response_type', "option"))
            genericXml.append(self._createXmlElement('preference', "button"))
            genericXml.append(self._createXmlElement('title', "Fast selection buttons"))

            buttonIndex = 0
            for buttonLabel, buttonValue in buttons.items():
                if buttonIndex < MAX_OPTIONS :
                    optionsXml = XML.Element('options')
                    optionsXml.append(self._createXmlElement('label', buttonLabel))
                    optionsXml.append(self._createXmlOption('value', buttonValue))
                    genericXml.append(optionsXml)
                else:
                    logger.warning('Number of buttons is larger then %s, ignoring: %s, %s', MAX_OPTIONS, buttonLabel, buttonLabel)
                buttonIndex += 1
            outputXml.append(genericXml)
            '''

            buttonIndex = 0
            for buttonLabel, buttonValue in buttons.items():
                if buttonIndex < MAX_OPTIONS :
                    # sanity check, string length 64 is the limit of WA
                    if len(buttonLabel) >64 :
                        buttonLabel = buttonLabel[:64]
                        logger.warning('Button label is > 64 char, truncating to: %s', buttonLabel)
                    if len(buttonValue) >64 :
                        buttonValue = buttonValue[:64]
                        logger.warning('Button label is > 64 char, truncating to: %s', buttonValue)

                    xmlSuggestion = XML.Element('suggestions', structure = 'listItem')
                    xmlLabel = XML.Element('label')
                    xmlLabel.text = buttonLabel
                    xmlValue = XML.Element('value')
                    xmlValue.text = buttonValue
                    xmlSuggestion.append(xmlLabel)
                    xmlSuggestion.append(xmlValue)
                    outputXml.append(xmlSuggestion)
                else:
                    logger.warning('Number of buttons is larger then %s, ignoring: %s, %s', MAX_OPTIONS, buttonLabel, buttonValue)
                buttonIndex += 1
        if foldables:
            #Example: {"output": {"text": "this is regular text", "more": [{"title": "this is title", "body": "this is body"}]}}
            foldableIndex = 0
            for foldableTitle, foldableBody in foldables.items():
                if foldableIndex < MAX_OPTIONS :
                    xmlFoldable = XML.Element('more', structure = 'listItem')
                    xmlTitle = XML.Element('title')
                    xmlTitle.text = foldableTitle
                    xmlBody = XML.Element('body')
                    xmlBody.text = foldableBody
                    xmlFoldable.append(xmlTitle)
                    xmlFoldable.append(xmlBody)
                    outputXml.append(xmlFoldable)
                else:
                    logger.warning('Number of foldables is larger then %s, ignoring: %s, %s', MAX_OPTIONS, foldableTitle, foldableBody)
                foldableIndex += 1
        return outputXml

    def _createContextElement(self, variables):
        contextXml = XML.Element('context')
        for name, value in variables.items():
            contextXml.append(self._createXmlElement(name, value))
        return contextXml

    def _createGotoElement(self, target, selector):
        gotoXml = XML.Element('goto')
        gotoXml.append(self._createXmlElement('target', target))
        gotoXml.append(self._createXmlElement('selector', selector))
        return gotoXml

    def _createXmlElement(self, name, value):
        if name=='values':
            xmlElement = XML.Element(name, structure='listItem')
        else:
            xmlElement = XML.Element(name)
        xmlElement.text = value
        return xmlElement

    def _createXmlOption(self, name, value):
        # optionsXml.append(self._createXmlElement('value', self._createXmlElement('input', self._createXmlElement('text'), buttonValue)))
        xmlValue = XML.Element(name)
        xmlInput = XML.Element('input')
        xmlIext = XML.Element('text')
        xmlValue.append(xmlInput)
        xmlInput.append(xmlIext)
        xmlIext.text = value
        return xmlValue

    def _concatenateOutputs(self, channelOutputs):
        output = u''
        for segment in channelOutputs:
            output += segment + u' '
        return output.strip()
