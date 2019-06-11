from wawCommons import getScriptLogger

logger = getScriptLogger(__file__)


class WorkspaceTest(object):


    '''
        engine
        language
        userID
        inputType
        input
        expectedTranscriptType
        returnedTranscriptType
        expectedTranscript
        returnedTranscript
        resultTranscript
        expectedIntentType
        returnedIntentType
        resultIntent
        expectedEntitiesType
        returnedEntitiesType
        expectedEntities
        returnedEntities
        resultEntities
        expectedOutputType
        returnedOutputType
        expectedOutput
        returnedOutput
        resultOutput
        expectedResponseType
        returnedResponseType
        expectedResponse
        returnedResponse
        resultResponse
        result
    '''

    def __init__(self):
        self.engine = ""
        self.language = ""
        self.userID = ""
        self.inputType = ""
        self.input = ""
        self.expectedTranscriptType = ""
        self.returnedTranscriptType = ""
        self.expectedTranscript = ""
        self.returnedTranscript = ""
        self.resultTranscript = ""
        self.expectedIntentType = ""
        self.returnedIntentType = ""
        self.expectedIntent = ""
        self.returnedIntent = ""
        self.resultIntent = ""
        self.expectedEntitiesType = ""
        self.returnedEntitiesType = ""
        self.expectedEntities = ""
        self.returnedEntities = ""
        self.resultEntities = ""
        self.expectedOutputType = ""
        self.returnedOutputType = ""
        self.expectedOutput = ""
        self.returnedOutput = ""
        self.resultOutput = ""
        self.expectedResponseType = ""
        self.returnedResponseType = ""
        self.expectedResponse = ""
        self.returnedResponse = ""
        self.resultResponse = ""
        self.result = ""


    def toRow(self, ordering):
        if ordering:
            print(self.__dict__)
            print(getattr(self, 'expectedIntent'))
            return [getattr(self, key) for key in ordering if key in self.__dict__]
        else:
            sys.exit(1)

    def getHeader(self):
        return [key for key in self.__dict__]
