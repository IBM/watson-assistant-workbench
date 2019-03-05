
import os, unittest

import wawCommons

class TestGetFilesAtPath(unittest.TestCase):
    
    ''' Tests if particular file is found by getFilesAtPath function '''
    def test_ifFileIsFound(self):
        directory = './tests/test_data' 
        pathList = wawCommons.getFilesAtPath([directory])
        testFile = os.path.abspath(os.path.join(directory, "text2codeExample-en.xml"))
        assert testFile in pathList
    