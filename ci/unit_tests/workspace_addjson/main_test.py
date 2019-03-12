
import os, unittest, sys, codecs, json

import workspace_addjson

class TestMain(unittest.TestCase):

    directory = './ci/unit_tests/workspace_addjson/main_data/'
    workspaceFile = 'workspace_forAddJsonTest.json'
    copycmd = 'cp ' + directory + 'workspace.json ' + directory + 'workspace_forAddJsonTest.json'

    def test_addingJsonDictionary(self):
        ''' Tests for including additional json dictionary to arbitrary location in dialog nodes '''
        # copy the workspace.json
        os.system(self.copycmd)

        jsonAddPath = self.directory + 'jsonToAdd.json'
        referenceResult = self.directory + 'workspace_result.json'
        targetKey = 'parent'

        workspace_addjson.main(['-w', self.workspaceFile, '-d', self.directory , '-j', jsonAddPath, '-t', targetKey, '-v'])

        # compare the new result with the reference result
        with codecs.open(os.path.join(self.directory, self.workspaceFile), 'r', encoding='utf8') as inputpath:
            newWorkspace = json.load(inputpath)

        with codecs.open(os.path.join(referenceResult), 'r', encoding='utf8') as inputpath:
            referenceWorkspace = json.load(inputpath)

        referenceWorkspaceString = json.dumps(referenceWorkspace)
        newWorkspaceString = json.dumps(newWorkspace)

        assert referenceWorkspaceString == newWorkspaceString

    def test_addingJsonArray(self):
        ''' Tests for including additional json array to arbitrary location in dialog nodes '''
        # copy the workspace.json
        os.system(self.copycmd)

        jsonAddPath = self.directory + 'jsonToAdd_array.json'
        referenceResult = self.directory + 'workspace_result_array.json'
        targetKey = 'parent'

        workspace_addjson.main(['-w', self.workspaceFile, '-d', self.directory , '-j', jsonAddPath, '-t', targetKey, '-v'])

        # compare the new result with the reference result
        with codecs.open(os.path.join(self.directory, self.workspaceFile), 'r', encoding='utf8') as inputpath:
            newWorkspace = json.load(inputpath)

        with codecs.open(os.path.join(referenceResult), 'r', encoding='utf8') as inputpath:
            referenceWorkspace = json.load(inputpath)

        referenceWorkspaceString = json.dumps(referenceWorkspace)
        newWorkspaceString = json.dumps(newWorkspace)

        assert referenceWorkspaceString == newWorkspaceString

    # TODO add more tests
    # files exists
