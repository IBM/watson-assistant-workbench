"""
Copyright 2019 IBM Corporation
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

from junitparser import Error

class _WAWBaseException(Exception):
    def toJson(self):
        if hasattr(self, 'message'):
            return { 'type': self.__class__.__name__, 'message': self.message }
        else:
            return { 'type': self.__class__.__name__ }

    def toJUnitError(self):
        return Error(self.message if hasattr(self, 'message') else '', self.__class__.__name__)

class CFCallException(_WAWBaseException):
    def __init__(self, function, package, response, leadingMessage=None, trailingMessage=None, kwargs={}):
        self.message = leadingMessage if leadingMessage else "Error"
        self.message += " from function '{}' in package '{}'".format(function, package)
        for key, value in kwargs.items():
             self.message += ", {} '{}'".format(key, value)
        self.message += ", status code '{}', response:\n'{}'".format(response.status_code, response.text)
        self.message += (", " + trailingMessage) if trailingMessage else ""
        super(CFCallException, self).__init__(self.message)

class CFCallStatusException(CFCallException):
    def __init__(self, function, package, response, kwargs={}):
        super(CFCallStatusException, self).__init__(function, package, response, "Unexpected response status", None, kwargs)
