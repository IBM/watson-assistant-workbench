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

import re
from wawCommons import eprintf
from collections import OrderedDict

try:
    unicode        # Python 2
except NameError:
    unicode = str  # Python 3


class NodeData(object):
    """ Represents a data structure containing all necessary information for a single dialog node
    """

    def __init__(self):
        self._channels = {}             # key: channel name, value: list of all outputs for the channel (channel corresponds to modality)
        self._variables = {}            # key: variable name, value: variable value (request for changes on context)
        self._jumptoTarget = None
        self._jumptoSelector = None
        self._rawOutputs = []           # list of all outputs from the right column of the Excel source
        self._buttons = OrderedDict()   # key: button label, value: full button value, MUST BE ORDERED!
        self._foldables = OrderedDict() # key: short text, value: long text
        self._node_name = ""            # Name of the node
        self._node_condition = ""       # text of the condition

    def setName(self, node_name):
        self._node_name = node_name

    def getName(self):
        return  self._node_name

    def setCondition(self, node_condition):
        self._node_condition = node_condition

    def getCondition(self):
        return self._node_condition

    def addChannelOutput(self, channelName, channelOutput):
        if channelName not in self._channels:
            self._channels[channelName] = []
        self._channels[channelName].append(channelOutput)

    def getChannelOutputs(self):
        return self._channels

    def addVariable(self, name, value):
        self._variables[name] = value

    def getVariables(self):
        return self._variables

    def setJumpTo(self, target, selector):
        target_name = target[1:] if target.startswith(u'#') else target

        self._jumptoTarget = target_name
        self._jumptoSelector = selector

    def getJumpToTarget(self):
        return self._jumptoTarget

    def getJumpToSelector(self):
        return self._jumptoSelector

    def addButton(self, label, value):
        self._buttons[label] = value

    def getButtons(self):
        return self._buttons

    def addFoldable(self, _short_text, _long_text):
        self._foldables[_short_text] = _long_text

    def getFoldable(self):
        return self._foldables

    def addRawOutput(self, rawOutputs, labelsMap):
        """ Read the raw output and store all data from it - 
            channel outputs, context variables and jumpto definitions. """
        self._rawOutputs.append(rawOutputs)
        if not isinstance(rawOutputs, tuple) or len(rawOutputs) < 1:
            eprintf('Warning: rawOutput does not contain any data: %s\n', rawOutputs)

        if len(rawOutputs) >= 1 and (isinstance(rawOutputs[0], (str, unicode))):
            items = re.split('%%', rawOutputs[0])
            self.__handleChannelDefinition('1'+items[0])
            for item_i in range(1, len(items)):
                item = items[item_i]
                if not item: continue
                if item.startswith(u'$'):
                    self.__handleVariableDefinition(item[1:])
                elif item.startswith(u'B'):
                    self.__handleButtonDefinition(item[1:])
                elif item.startswith(u'F'):
                    self.__handleFoldableDefinition(item[1:])
                elif item.startswith(u':'):
                    self.__handleJumpToDefinition(item[1:], labelsMap)
                else:
                    self.__handleChannelDefinition(item)

        if len(rawOutputs) >= 2:
            if rawOutputs[1]:
                self.__handleButtonDefinition(rawOutputs[1])
            if rawOutputs[2]:
                self.__handleJumpToDefinition(rawOutputs[2], labelsMap)

    def __handleVariableDefinition(self, variables):
        for varAssignment in re.split(';', variables):
            keyAndValue = re.split('=', varAssignment)
            if len(keyAndValue) == 2:
                self.addVariable(keyAndValue[0], keyAndValue[1])

    def __handleJumpToDefinition(self, jumpto, labelsMap):
        selector = 'user_input'
        label = jumpto
        if len(jumpto) > 2 and jumpto[1] == '_':
            label = jumpto[2:]
            if jumpto[0] == 'b':
                selector = 'body'
            elif jumpto[0] == 'c':
                selector = 'condition'
        self.setJumpTo(label, selector) # this is the first path through, we leave labels in target
        #labels will be replaced by node_names during the second path

    def __handleChannelDefinition(self, channel):
        channelValue = channel

        if len(channel) > 0 and isinstance(channel, (str, unicode)):
            #channel = channel.decode('utf-8')
            channelName = channel[0]
            channelValue = channel[1:]
            if channelName.isdigit():
                channelName = channel[0]
                channelValue = channel[1:]
            self.addChannelOutput(channelName, channelValue)

    def __handleButtonDefinition(self, buttons):
        for button in re.split(';', buttons):
            labelAndValue = re.split('=', button)
            if len(labelAndValue) == 2:
                self.addButton(labelAndValue[0].strip(), labelAndValue[1].strip())

    def __handleFoldableDefinition(self, foldables):
        for button in re.split(';', foldables):
            shortAndLong = re.split('=', button)
            if len(shortAndLong) == 2:
                self.addFoldable(shortAndLong[0].strip(), shortAndLong[1].strip())
