# coding: utf-8
from __future__ import print_function
import unittest
from scripts.XMLHandler import XMLHandler
import scripts.DialogData as Dialog
'''
Created on Jan 16, 2018
@author: alukes
'''

DOMAIN = u'G_TEST'


class XMLHandlerTest(unittest.TestCase):


    def setUp(self):
        self._handler = XMLHandler()


    def tearDown(self):
        self._handler = None


    def test_positive_convertMainChannelOutputToXml(self):
        """ Convert Dialog data with just channel outputs into XML. """
        labels = {}
        dialogData = Dialog.DialogData()
        intentData = dialogData.getIntentData(u'HELP_①', DOMAIN)
        intentData.addExample(u'I need help.')
        intentData.addExample(u'Can you help me?')
        intentData.addRawOutput([u'Sure.①'], labels)
        intentData.addRawOutput([u'Sorry, cannot help you.'], labels)
        intentData.addRawOutput([u'Let us see, what is your problem?'], labels)
        intents = [u'HELP_①']

        xmlDocument = self._handler.convertDialogData(dialogData, intents)
        actual = self._handler.printXml(xmlDocument, False)
        expected = (u'<nodes><node name="HELP_①"><condition>#HELP_①</condition><output><textValues><values>Sure.①</values>'
            u'<values>Sorry, cannot help you.</values><values>Let us see, what is your problem?</values>'
            u'</textValues></output></node></nodes>')
        self.assertEquals(actual, expected)


    def test_positive_convertMultipleChannelOutputsToXml(self):
        """ Convert Dialog data with just channel outputs into XML. """
        labels = {}
        dialogData = Dialog.DialogData()
        intentData = dialogData.getIntentData(u'HELP_①', DOMAIN)
        intentData.addExample(u'I need help.')
        intentData.addExample(u'Can you help me?')
        intentData.addRawOutput([u'Sure.①'], labels)
        intentData.addRawOutput([u'Sorry, cannot help you.%%260 seconds'], labels)
        intentData.addRawOutput([u'Let us see, what is your problem?%%7image.png%%8some URL'], labels)
        intents = [u'HELP_①']

        xmlDocument = self._handler.convertDialogData(dialogData, intents)
        actual = self._handler.printXml(xmlDocument, False)
        expected = (u'<nodes><node name="HELP_①"><condition>#HELP_①</condition><output><textValues><values>Sure.①</values>'
            u'<values>Sorry, cannot help you.</values><values>Let us see, what is your problem?</values>'
            u'</textValues><url>some URL</url><timeout>60 seconds</timeout><graphics>image.png</graphics>'
            u'</output></node></nodes>')
        self.assertEquals(actual, expected)


    def test_positive_convertConetxtToXml(self):
        """ Convert Dialog data with just context into XML. """
        dialogData = Dialog.DialogData()
        intentData = dialogData.getIntentData(u'HELP_①', DOMAIN)
        intentData.addChannelOutput(u'1', u'Hi.')
        intentData.addVariable(u'var1', u'①')
        intentData.addVariable(u'var2', u'value')
        intents = [u'HELP_①']

        xmlDocument = self._handler.convertDialogData(dialogData, intents)
        actual = self._handler.printXml(xmlDocument, False)
        expected = (u'<nodes><node name="HELP_①"><condition>#HELP_①</condition><output><textValues><values>Hi.</values></textValues></output><context><var1>①</var1><var2>value</var2>'
                    u'</context></node></nodes>')
        self.assertEquals(actual, expected)


    def test_positive_convertGotoToXml(self):
        """ Convert Dialog data with Goto and channel into XML. """
        dialogData = Dialog.DialogData()
        intentData = dialogData.getIntentData(u'HELP_①', DOMAIN)
        intentData.addChannelOutput(u'1', u'Hi.')
        intentData.setJumpTo(u'label①', u'condition')
        intents = [u'HELP_①']

        xmlDocument = self._handler.convertDialogData(dialogData, intents)
        actual = self._handler.printXml(xmlDocument, False)
        expected = (u'<nodes><node name="HELP_①"><condition>#HELP_①</condition><output><textValues><values>Hi.</values></textValues></output><goto><target>label①</target>'
                    u'<selector>condition</selector></goto></node></nodes>')
        self.assertEquals(actual, expected)

    
    def test_positive_convertDialogDataToXml(self):
        """ Convert Dialog data containing all types of segments into XML. """
        labels = {}
        dialogData = Dialog.DialogData()
        intentData = dialogData.getIntentData(u'HELP_①', DOMAIN)
        intentData.addExample(u'I need help.')
        intentData.addExample(u'Can you help me?')
        intentData.addRawOutput([u'Sure.①'], labels)
        intentData.addRawOutput([u'Sorry, cannot help you.%%360 seconds'], labels)
        intentData.addRawOutput([u'Let us see, what is your problem?%%7image.jpg%%8my_URL'], labels)
        intentData.addVariable(u'var1', u'some ①')
        intentData.addVariable(u'var2', u'other value')
        intentData.setJumpTo(u'label_①', u'user input')
        intents = [u'HELP_①']

        xmlDocument = self._handler.convertDialogData(dialogData, intents)
        actual = self._handler.printXml(xmlDocument, False)
        expected = (u'<nodes><node name="HELP_①"><condition>#HELP_①</condition><output><textValues><values>Sure.①</values>'
                    u'<values>Sorry, cannot help you.</values><values>Let us see, what is your problem?</values>'
                    u'</textValues><url>my_URL</url><sound>60 seconds</sound><graphics>image.jpg</graphics></output>'
                    u'<context><var1>some ①</var1><var2>other value</var2></context><goto><target>label_①</target>'
                    u'<selector>user input</selector></goto></node></nodes>')
        self.assertEquals(actual, expected)


    def test_positive_convertDialogDataSelectedIntentsOnly(self):
        """ Convert Dialog data with just channel outputs into XML. """
        labels = {}
        dialogData = Dialog.DialogData()
        intentData = dialogData.getIntentData(u'HELP_1', DOMAIN)
        intentData.addExample(u'I need help.')
        intentData.addRawOutput(u'Sure.', labels)
        intentData = dialogData.getIntentData(u'HELP_2', DOMAIN)
        intentData.addExample(u'Can you help me?')
        intentData.addRawOutput([u'Sorry, cannot help you.'], labels)
        intents = [u'HELP_2']

        xmlDocument = self._handler.convertDialogData(dialogData, intents)
        actual = self._handler.printXml(xmlDocument, False)
        expected = (u'<nodes><node name="HELP_2"><condition>#HELP_2</condition><output><textValues>'
                    u'<values>Sorry, cannot help you.</values></textValues></output></node></nodes>')
        print(actual)
        print(expected)
        self.assertEquals(actual, expected)


if __name__ == "__main__":
    unittest.main()
