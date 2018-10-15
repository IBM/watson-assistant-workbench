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

from IntentData import IntentData
from EntityData import EntityData
from NodeData import NodeData
import unicodedata, unidecode
from wawCommons import printf, eprintf, toIntentName
X_PLACEHOLDER = u'&lt;x&gt;'

class DialogData(object):
    """ DialogData represents complete dialog (intents, entities, nodes, labels).
    The data are collected across all processed T2C source.
        _domains keeps track how domains are affiliated to nodes as we generate separate xls for each domain
        concept of domain correspods to a single Excel Workbook
    """

    def __init__(self, config):
        # we store on bag of intents and one bag of entities (each results in one file all in corresponding directory
        self._labelsMap = {} # key: lable, value - node name - translation table for generating jumps

        self._entities = {}  # key: entity name, value: list of all Dialog entity options; entities is a flat list over all the domains
        self._intents = {}   # key: intent name, value: IntentData object; intents is a flat list over all the domains

        # nodes are grouped based on domain
        self._nodes = {}     # key: node name, value: list of all associated dialog nodes
        self._domains = {}   # key: domain name, value: list of all associated nodes with the given domain

        self._config= config            #we need config to get NAME_POLICY, verbosity,..
        self._VERBOSE = hasattr(config, 'common_verbose')
        self._NAME_POLICY = 'soft'      # TBD: enable to set the NamePolicy from config file

    #  LABEL
    #******************************************

    def addLabel(self, label, node_name):
        self._labelsMap[label] = node_name

    def isLabel(self, label):
        # Checks if label exists
        return (label in self._labelsMap)

    def getLabelsMap(self):
        """ Return map with GoTo labels as keys and target  node_names as values. """
        return self._labelsMap

    #  ENTITY
    #******************************************

    def createEntity(self, entity_name):
    # Return entity of a given entityName or None, if entity exists
        if entity_name not in self._entities:
            self._entities[entity_name] = EntityData()
            return self._entities[entity_name]
        else:
            return None

    def getAllEntities(self):
        return self._entities

    #   INTENT
    #******************************************

    def createIntent(self, intent_name):
        # return intent of a given intentName (if it does not exist it creates an empty one )
        if intent_name not in self._intents:
            self._intents[intent_name] = IntentData()
        return self._intents[intent_name]

    def getAllIntents(self):
        return self._intents

    #   NODE
    #******************************************

    def createNode(self, node_name, domain_name=None):
        """ Creates empty node and links it to DialogData.NodeData, returns 0 if already exists
            - extends _domains if  domainName is not in yet
        """
        # Update domain structure, add node to corresponding domain
        if domain_name is not None:
            # make sure the domain is registered
            if domain_name not in self._domains:
                self._domains[domain_name] = []
            # make sure the nodeName is remembered within the domain
            #if node_name not in self._nodes[domain_name]:
            if node_name not in self._domains[domain_name]:
                    self._domains[domain_name].append(node_name)

        # Update nodes structure, if node is not there yet - add it
        if node_name not in self._nodes:
            self._nodes[node_name] = NodeData()
            return self._nodes[node_name]
        else:
            return None

    def getNode(self, node_name):
        """  @:returns node of a given name or None
        """
        if node_name not in self._nodes:
            return None
        return self._nodes[node_name]

    def getAllNodes(self):
        """  @:returns list of all nodes
        """
        return self._nodes

    def updateReferencesNodes(self):
        """
            Replaces labels by known target node_names
            This is implementation of the second path through the dialogData.
        """

        for node_name in self._nodes: #for each node in the domain
            nodeData = self.getNode(node_name)
            if nodeData and nodeData._jumptoTarget:
                label = nodeData._jumptoTarget
                if label in self._labelsMap:
                    node_target= self._labelsMap[label]
                    nodeData._jumptoTarget= node_target
                    printf('INFO: Resolving cross reference label:%s -> node_name:%s)\n', label, node_name)
                else:
                    printf('INFO: Label:%s not resolve, expecting tahat label is external node_name\n', label)

#   DOMAINS
#******************************************
    def getAllDomains(self):
        return self._domains

# createUnique ..
#******************************************
    def createUniqueIntentName(self, intent_name):
        """
            Creates unique intent_name based on given string
              intent_name is stripped from not allowed characters, spaces are replaced by _
              if the result exists a modifier is added at the end of the string

              :returns unique intent_name or None if not able to create
        """
        #Normalize the string
        unaccented_name=unicodedata.normalize('NFKD', intent_name).encode('ASCII', 'ignore')  # remove accents
        unique_intent_name = toIntentName( self._NAME_POLICY, None, unaccented_name).decode('utf-8')
        if unique_intent_name not in self._intents:
            return unique_intent_name
        #try to modify by a number
        for modifier in range(0, 10000):
            new_unique_intent_name=unique_intent_name+repr(modifier)  #create a modified one
            # Check if the name exists
            if new_unique_intent_name not in self._intents:
                return new_unique_intent_name
        return None

    def createUniqueEntityName(self, entity_name):
        """
            Creates unique entity_name based on given string
              intent_name is stripped from not allowed characters, spaces are replaced by _
              if the result exists a modifier is added at the end of the string

              :returns unique intent_name or None if not able to create
        """
        #Normalize the string
        unaccented_name=unicodedata.normalize('NFKD', entity_name).encode('ASCII', 'ignore')  # remove accents
        unique_entity_name = toIntentName(self._NAME_POLICY, None, unaccented_name).decode('utf-8')
        if unique_entity_name not in self._entities:
            return unique_entity_name
        #try to modify by a number
        for modifier in range(0, 10000):
            new_unique_entity_name= unique_entity_name + repr(modifier)  #create a modified one
            # Check if the name exists
            if new_unique_entity_name not in self._intents:
                return new_unique_entity_name
        return None

    def createUniqueNodeName(self, node_name):
        """
            Creates unique node_name based on given string
              node_name is stripped from not allowed characters, spaces are replaced by _
              if the result exists a modifier is added at the end of the string

              :returns unique node_name or None if not able to create
        """
        # Normalize the string
        unaccented_name=unicodedata.normalize('NFKD', node_name).encode('ASCII', 'ignore')  # remove accents
        unique_node_name = toIntentName(self._NAME_POLICY, None, unaccented_name).decode('utf-8').upper()
        if unique_node_name not in self._nodes:
            return unique_node_name
        # try to modify by a number
        for modifier in range(0, 10000):
            new_unique_node_name = unique_node_name + '_' + repr(modifier)  # create a modified one
            # Check if the name exists
            if new_unique_node_name not in self._nodes:
                return new_unique_node_name
        return None
