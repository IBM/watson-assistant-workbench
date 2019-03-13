
import os, unittest, sys, codecs, json

import workspace_addjson

class TestIncludeJson(unittest.TestCase):

    def test_checkingNotExistingKey(self):
        ''' Tests for checking missing JSON key when calling includeJson function '''

        nodeJSON = {
            "a" : "b"
        }
        keyJSON = "c"
        keySearch = "a"
        includeJSON = {
            "x" : "y"
        }

        resultJSON = nodeJSON

        workspace_addjson.includeJson(nodeJSON, keyJSON, keySearch, includeJSON)

        assert resultJSON == nodeJSON

    # TODO write more tests
    # keyJSON = None
    # keyJSON = "value"
