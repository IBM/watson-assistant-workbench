# coding: utf-8
import os, unittest
from scripts.XLSXHandler import XLSXHandler
import scripts.DialogData as Dialog
'''
Created on Jan 12, 2018
@author: alukes
'''

DOMAIN = u'G_TEST'
PREFIX = u'SHEET'


class XLSXHandlerTest(unittest.TestCase):


    def setUp(self):
        self._handler = XLSXHandler()


    def tearDown(self):
        self._handler = None


    def test_positive_parseXLSXIntoDataBlocks(self):
        """ Verify that we can parse the testing XLSX containing all definitions we currently support. """

        filename = 'data/G_TEST.xlsx'
        if not os.path.exists(filename):
            filename = 'test/' + filename
        self.assertTrue(os.path.exists(filename))

        self._handler.parseXLSXIntoDataBlocks(filename)
        dialogData = self._handler.getDialogData()
        dataBlocks = self._handler.getDataBlocks()

        self.assertTrue(dialogData)
        self.assertTrue(dataBlocks)
        self.assertEquals(len(dataBlocks), 11)

        # block 1
        dataTuple = dataBlocks[0]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'POMOC')
        block = dataTuple[3]
        self.assertEquals(len(block), 3)
        self.assertEquals(block[0][0], '#POMOC')
        self.assertFalse(block[0][1])

        # block 2
        dataTuple = dataBlocks[1]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'POMOC2')
        block = dataTuple[3]
        self.assertEquals(len(block), 2)
        self.assertEquals(block[0][0], '#POMOC2')
        self.assertFalse(block[0][1])

        # block 3
        dataTuple = dataBlocks[2]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'G_TEST_SHEET_JAKE_BUDE_POCASI')
        block = dataTuple[3]
        self.assertEquals(len(block), 3)
        self.assertEquals(block[0][0], 'jake bude pocasi?')
        self.assertTrue(block[0][1])

        # block 4
        dataTuple = dataBlocks[3]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'sdjkhdsf &&  #POMOC && @OBDOBI:leto')
        block = dataTuple[3]
        self.assertEquals(len(block), 3)
        self.assertEquals(block[0][0], 'sdjkhdsf &&  #POMOC && @OBDOBI:<x>')
        self.assertTrue(Dialog.X_PLACEHOLDER in block[0][0])
        self.assertFalse(block[0][1])

        # block 5
        dataTuple = dataBlocks[4]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'Hello && #POMOC')
        block = dataTuple[3]
        self.assertEquals(len(block), 2)
        self.assertEquals(block[0][0], 'Hello && #POMOC')
        self.assertFalse(block[0][1])

        # block 6
        dataTuple = dataBlocks[5]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'POMOC2')
        block = dataTuple[3]
        self.assertEquals(len(block), 2)
        self.assertEquals(block[0][0], '#POMOC2')
        self.assertTrue(block[0][1])

        # block 7
        dataTuple = dataBlocks[6]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'ORDER_COOKIE')
        block = dataTuple[3]
        self.assertEquals(len(block), 4)
        self.assertEquals(block[0][0], '#ORDER_COOKIE')
        self.assertFalse(block[0][1])

        # block 8
        dataTuple = dataBlocks[7]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'WHAT_TO_DO')
        block = dataTuple[3]
        self.assertEquals(len(block), 3)
        self.assertEquals(block[0][0], '#WHAT_TO_DO')
        self.assertFalse(block[0][1])

        # block 9
        dataTuple = dataBlocks[8]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'WHAT_TO_EAT')
        block = dataTuple[3]
        self.assertEquals(len(block), 3)
        self.assertEquals(block[0][0], '#WHAT_TO_EAT')
        self.assertFalse(block[0][1])

        # block 10
        dataTuple = dataBlocks[9]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'WHAT_TO_COOK')
        block = dataTuple[3]
        self.assertEquals(len(block), 3)
        self.assertEquals(block[0][0], '#WHAT_TO_COOK')
        self.assertFalse(block[0][1])

        # block 11
        dataTuple = dataBlocks[10]
        self.assertEquals(dataTuple[0], DOMAIN)
        self.assertEquals(dataTuple[1], PREFIX)
        self.assertEquals(dataTuple[2], u'WHAT_TO_BURN')
        block = dataTuple[3]
        self.assertEquals(len(block), 3)
        self.assertEquals(block[0][0], '#WHAT_TO_BURN')
        self.assertFalse(block[0][1])

        entities = dialogData.getAllEntities()
        self.assertEquals(len(entities), 2)
        self.assertEquals(entities[u'OBDOBI'], [u'jaro', u'leto', u'podzim', u'zima'])
        self.assertEquals(entities[u'TYP_DOTAZU'], [u'dest;prsi;leje', u'snih;snezi;chumeli'])


    def test_positive_convertBlocksToDialogData_standardIntent(self):
        """ Verify handling of standard intent block starting with '#'. """

        block = ((u'#HELP_①', None), (u'Can you help me?', u'Sure I can ①.'), (u'I need help ①.', u'How can I help?'))
        self._handler.addDataBlock((DOMAIN, PREFIX, u'HELP_①', block))
        self._handler.convertBlocksToDialogData()

        dialogData = self._handler.getDialogData()
        self.assertEquals(len(dialogData.getAllEntities()), 0)

        self.assertEquals(len(dialogData.getAllIntents()), 1)
        intentData = dialogData.getAllIntents()[u'HELP_①']
        self.assertTrue(intentData)
        self.assertEquals(len(intentData.getIntentAlternatives()), 2)
        self.assertEquals(intentData.getIntentAlternatives()[0], u'Can you help me?')
        self.assertEquals(intentData.getIntentAlternatives()[1], u'I need help ①.')
        self.assertEquals(len(intentData.getChannelOutputs()), 1)
        mainTextOutputs = intentData.getChannelOutputs()['1']
        self.assertEquals(len(mainTextOutputs), 2)
        self.assertEquals(mainTextOutputs[0], u'Sure I can ①.')
        self.assertEquals(mainTextOutputs[1], u'How can I help?')
        self.assertFalse(intentData.getJumpToSelector())
        self.assertFalse(intentData.getJumpToTarget())
        self.assertEquals(len(intentData.getVariables()), 0)

        self.assertEquals(len(dialogData.getDomains()), 1)
        domainIntents = dialogData.getDomains()[DOMAIN]
        self.assertEquals(len(domainIntents), 1)
        self.assertEquals(domainIntents[0], u'HELP_①')


    def test_positive_convertBlocksToDialogData_intentWithNoHash(self):
        """ Verify handling of intent block not having '#' at the beginning. """

        block = ((u'How is the weather tomorrow?', u'Good.'), (u'Hey what is the forecast today?', u'Pretty bad.'), (None, u'I wish I knew_①.'))
        self._handler.addDataBlock((DOMAIN, PREFIX, u'G_TEST_SHEET_HOW_IS_THE_WEATHER_TOMORROW', block))
        self._handler.convertBlocksToDialogData()

        dialogData = self._handler.getDialogData()
        self.assertEquals(len(dialogData.getAllEntities()), 0)

        self.assertEquals(len(dialogData.getAllIntents()), 1)
        intentData = dialogData.getAllIntents()[u'G_TEST_SHEET_HOW_IS_THE_WEATHER_TOMORROW']
        self.assertTrue(intentData)
        self.assertEquals(len(intentData.getIntentAlternatives()), 2)
        self.assertEquals(intentData.getIntentAlternatives()[0], u'How is the weather tomorrow?')
        self.assertEquals(intentData.getIntentAlternatives()[1], u'Hey what is the forecast today?')
        self.assertEquals(len(intentData.getChannelOutputs()), 1)
        mainTextOutputs = intentData.getChannelOutputs()['1']
        self.assertEquals(len(mainTextOutputs), 3)
        self.assertEquals(mainTextOutputs[0], u'Good.')
        self.assertEquals(mainTextOutputs[1], u'Pretty bad.')
        self.assertEquals(mainTextOutputs[2], u'I wish I knew_①.')
        self.assertFalse(intentData.getJumpToSelector())
        self.assertFalse(intentData.getJumpToTarget())
        self.assertEquals(len(intentData.getVariables()), 0)

        self.assertEquals(len(dialogData.getDomains()), 1)
        domainIntents = dialogData.getDomains()[DOMAIN]
        self.assertEquals(len(domainIntents), 1)
        self.assertEquals(domainIntents[0], u'G_TEST_SHEET_HOW_IS_THE_WEATHER_TOMORROW')


    def test_positive_convertBlocksToDialogData_intentOnly(self):
        """ Verify handling of intent block that creates no dialog nodes and specifies just intent alternatives. """

        block = ((u'#HELP_①', None), (u'Can you help me?', None), (u'I need help ①.', None))
        self._handler.addDataBlock((DOMAIN, PREFIX, u'HELP_①', block))
        self._handler.convertBlocksToDialogData()

        dialogData = self._handler.getDialogData()
        self.assertEquals(len(dialogData.getAllEntities()), 0)

        self.assertEquals(len(dialogData.getAllIntents()), 1)
        intentData = dialogData.getAllIntents()[u'HELP_①']
        self.assertTrue(intentData)
        self.assertEquals(len(intentData.getIntentAlternatives()), 2)
        self.assertEquals(intentData.getIntentAlternatives()[0], u'Can you help me?')
        self.assertEquals(intentData.getIntentAlternatives()[1], u'I need help ①.')
        self.assertEquals(len(intentData.getChannelOutputs()), 0)
        self.assertFalse(intentData.getJumpToSelector())
        self.assertFalse(intentData.getJumpToTarget())
        self.assertEquals(len(intentData.getVariables()), 0)

        self.assertEquals(len(dialogData.getDomains()), 1)
        domainIntents = dialogData.getDomains()[DOMAIN]
        self.assertEquals(len(domainIntents), 1)
        self.assertEquals(domainIntents[0], u'HELP_①')


    def test_positive_convertBlocksToDialogData_nodeOnly(self):
        """ Verify handling of node only intent block. This block requires that the intent has been defined earlier. """

        block = ((u'#HELP_①', None), (u'I need help ①.', None))
        self._handler.addDataBlock((DOMAIN, PREFIX, u'HELP_①', block))
        block = ((u'#HELP_①', u'Sure I can ①.'), (None, u'How can I help?'))
        self._handler.addDataBlock((DOMAIN, PREFIX, u'HELP_①', block))
        self._handler.convertBlocksToDialogData()

        dialogData = self._handler.getDialogData()
        self.assertEquals(len(dialogData.getAllEntities()), 0)

        self.assertEquals(len(dialogData.getAllIntents()), 1)
        intentData = dialogData.getAllIntents()[u'HELP_①']
        self.assertTrue(intentData)
        self.assertEquals(len(intentData.getIntentAlternatives()), 1)
        self.assertEquals(intentData.getIntentAlternatives()[0], u'I need help ①.')
        self.assertEquals(len(intentData.getChannelOutputs()), 1)
        mainTextOutputs = intentData.getChannelOutputs()['1']
        self.assertEquals(len(mainTextOutputs), 2)
        self.assertEquals(mainTextOutputs[0], u'Sure I can ①.')
        self.assertEquals(mainTextOutputs[1], u'How can I help?')
        self.assertFalse(intentData.getJumpToSelector())
        self.assertFalse(intentData.getJumpToTarget())
        self.assertEquals(len(intentData.getVariables()), 0)

        self.assertEquals(len(dialogData.getDomains()), 1)
        domainIntents = dialogData.getDomains()[DOMAIN]
        self.assertEquals(len(domainIntents), 1)
        self.assertEquals(domainIntents[0], u'HELP_①')


    def test_positive_convertBlocksToDialogData_conditionBlock(self):
        """ Verify handling of entity block. """

        block = ((u'Hello && #HELP && @CAR:<x>', None),
                 (u'BMW⓫', u'What is wrong with your BMW⓫?'),
                 (None, u'Something wrong with your BMW⓫?'),
                 (u'Ford', u'What is wrong with your Ford?'),
                 (None, u'Something wrong with your Ford?'))
        self._handler.addDataBlock((DOMAIN, PREFIX, u'Hello && #HELP && @CAR:BMW⓫', block))
        self._handler.convertBlocksToDialogData()

        dialogData = self._handler.getDialogData()
        self.assertEquals(len(dialogData.getAllEntities()), 0)

        intents = dialogData.getAllIntents()
        self.assertEquals(len(intents), 2)
        intentData = intents[u'Hello && #HELP && @CAR:BMW⓫']
        self.assertTrue(intentData)
        self.assertEquals(len(intentData.getIntentAlternatives()), 0)
        self.assertEquals(len(intentData.getChannelOutputs()), 1)
        mainTextOutputs = intentData.getChannelOutputs()['1']
        self.assertEquals(len(mainTextOutputs), 2)
        self.assertEquals(mainTextOutputs[0], u'What is wrong with your BMW⓫?')
        self.assertEquals(mainTextOutputs[1], u'Something wrong with your BMW⓫?')
        self.assertFalse(intentData.getJumpToSelector())
        self.assertFalse(intentData.getJumpToTarget())
        self.assertEquals(len(intentData.getVariables()), 0)

        intentData = intents[u'Hello && #HELP && @CAR:Ford']
        self.assertTrue(intentData)
        self.assertEquals(len(intentData.getIntentAlternatives()), 0)
        self.assertEquals(len(intentData.getChannelOutputs()), 1)
        mainTextOutputs = intentData.getChannelOutputs()['1']
        self.assertEquals(len(mainTextOutputs), 2)
        self.assertEquals(mainTextOutputs[0], u'What is wrong with your Ford?')
        self.assertEquals(mainTextOutputs[1], u'Something wrong with your Ford?')
        self.assertFalse(intentData.getJumpToSelector())
        self.assertFalse(intentData.getJumpToTarget())
        self.assertEquals(len(intentData.getVariables()), 0)

        self.assertEquals(len(dialogData.getDomains()), 1)
        domainIntents = dialogData.getDomains()[DOMAIN]
        self.assertEquals(len(domainIntents), 2)
        self.assertEquals(domainIntents[0], u'Hello && #HELP && @CAR:BMW⓫')
        self.assertEquals(domainIntents[1], u'Hello && #HELP && @CAR:Ford')


    def test_positive_convertBlocksToDialogData_unknownIntent(self):
        """ Verify that node only blocks works for unknown intent as well. """

        block = ((u'#HELP_①', u'Sure I can ①.'), (None, u'How can I help?'))
        self._handler.addDataBlock((DOMAIN, PREFIX, u'#HELP_①', block))
        self._handler.convertBlocksToDialogData()

        dialogData = self._handler.getDialogData()
        self.assertEquals(len(dialogData.getAllEntities()), 0)
        self.assertEquals(len(dialogData.getAllIntents()), 1)
        intentData = dialogData.getAllIntents()[u'#HELP_①']
        self.assertTrue(intentData)
        self.assertEquals(len(intentData.getIntentAlternatives()), 0)
        self.assertEquals(len(intentData.getChannelOutputs()), 1)
        mainTextOutputs = intentData.getChannelOutputs()['1']
        self.assertEquals(len(mainTextOutputs), 2)
        self.assertEquals(mainTextOutputs[0], u'Sure I can ①.')
        self.assertEquals(mainTextOutputs[1], u'How can I help?')
        self.assertFalse(intentData.getJumpToSelector())
        self.assertFalse(intentData.getJumpToTarget())
        self.assertEquals(len(intentData.getVariables()), 0)

        self.assertEquals(len(dialogData.getDomains()), 1)
        domainIntents = dialogData.getDomains()[DOMAIN]
        self.assertEquals(len(domainIntents), 1)
        self.assertEquals(domainIntents[0], u'#HELP_①')


    def test_positive_complexCase2columnFormatBlock(self):
        # TBD
        pass


    def test_positive_complexCase4columnFormatBlock(self):
        """ Verify handling of 4-column block. """

        block = ((u'I don\'t know what to do', u'That is understandable.',
                    u'he has been moved=he has just been moved into the hospital;\nsomething else=it is something else', u'S1'),)
        self._handler.addDataBlock((DOMAIN, PREFIX, u'MY_INTENT', block))
        self._handler.addLabel(u'S1', u'MY_JUMPTO_INTENT')
        self._handler.convertBlocksToDialogData()

        dialogData = self._handler.getDialogData()
        self.assertEquals(len(dialogData.getAllEntities()), 0)

        self.assertEquals(len(dialogData.getAllIntents()), 1)
        intentData = dialogData.getAllIntents()[u'MY_INTENT']
        self.assertTrue(intentData)
        self.assertEquals(len(intentData.getIntentAlternatives()), 1)
        self.assertEquals(intentData.getIntentAlternatives()[0], u'I don\'t know what to do')
        self.assertEquals(len(intentData.getChannelOutputs()), 1)
        mainTextOutputs = intentData.getChannelOutputs()['1']
        self.assertEquals(len(mainTextOutputs), 1)
        self.assertEquals(mainTextOutputs[0], u'That is understandable.')
        self.assertEquals(intentData.getJumpToSelector(), u'user_input')
        self.assertEquals(intentData.getJumpToTarget(), u'MY_JUMPTO_INTENT')
        self.assertEquals(len(intentData.getVariables()), 0)
        buttons = intentData.getButtons()
        self.assertEquals(len(buttons), 2)
        self.assertEquals(buttons[u'he has been moved'], u'he has just been moved into the hospital')
        self.assertEquals(buttons[u'something else'], u'it is something else')

        self.assertEquals(len(dialogData.getDomains()), 1)
        domainIntents = dialogData.getDomains()[DOMAIN]
        self.assertEquals(len(domainIntents), 1)
        self.assertEquals(domainIntents[0], u'MY_INTENT')


if __name__ == "__main__":
    unittest.main()
