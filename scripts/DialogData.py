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

X_PLACEHOLDER = '<x>'

class DialogData(object):
    """ Represents complete Dialog data structure. """


    def __init__(self):
        self._intents = {}  # key: intent name, value: IntentData object
        self._entities = {}  # key: entity name, value: list of all Dialog entity options
        self._domains = {}  # key: domain name, value: list of all associated Dialog intents


    def getEntity(self, entityName):
        if entityName not in self._entities:
            self._entities[entityName] = []
        return self._entities[entityName]


    def getAllEntities(self):
        return self._entities


    def getIntentData(self, intentName, domainName=None):
        if domainName is not None:
            if domainName not in self._domains:
                self._domains[domainName] = []
            if intentName not in self._domains[domainName]:
                self._domains[domainName].append(intentName)

        if intentName not in self._intents:
            self._intents[intentName] = IntentData()
        return self._intents[intentName]


    def getAllIntents(self):
        return self._intents


    def getDomains(self):
        return self._domains
