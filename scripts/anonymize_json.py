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
from __future__ import print_function

import json, sys, argparse, os, random, string, re
from wawCommons import printf, eprintf

try:
    basestring            # Python 2
except NameError:
    basestring = (str, )  # Python 3

anonymizedKeys = ["text", "textValues", "values", "name", "title", "last_action",
 "repeat", "paraphrase"]
anonymizedStrings1 = ["destination", "origin", "navigation-directions-context",
 "navigation-directions"]
#anonymizedStrings2 = ["fourwheeldrive", "unlockdoor", "airbag", "phoneadaptor",
# "drivingmanual", "washerfluid"]
anonymizedStrings3 = [ "addedQuantities", "agent_action", "agreementContext", "alcoholic",
 "askFamily", "chosenRestaurant", "currentFlavour", "discussionAwareness",
 "flavorRecommendation", "flavours",
 "flavoursValues", "hasAlcoholicFlavour", "iceCream", "icecream", "iceCreamRecommendation",
 "isChild", "numeric_value", "oneOfEach", "orderingAllowed", "quantities",
 "quantitiesValues", "quantityRecommendation", "recommendationContext",
 "restaurant_recommendation", "servingstyle", "shouldAskOthers",
 "skillAction", "standardQuantity", "thisUsersOrderComplete"]

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def anonymize(nodeJSON, keyJSON, listAnonymize=None):

    # None
    if nodeJSON[keyJSON] is None:
        pass
    # list
    elif isinstance(nodeJSON[keyJSON], list):
        for i in range(len(nodeJSON[keyJSON])):
            listItemJSON = nodeJSON[keyJSON][i]
            if keyJSON in anonymizedKeys:
                anonymize(nodeJSON[keyJSON], i,True)
            else:
                anonymize(nodeJSON[keyJSON], i)
    # dict
    elif isinstance(nodeJSON[keyJSON], dict):
        for subKeyJSON in nodeJSON[keyJSON]:
            anonymize(nodeJSON[keyJSON], subKeyJSON)
    # string
    elif isinstance(nodeJSON[keyJSON], basestring):
        if keyJSON in anonymizedKeys or listAnonymize:
            nodeJSON[keyJSON] = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))
    # bool
    elif isinstance(nodeJSON[keyJSON], bool):
        pass
    # int, long, float, complex
    elif isNumber(nodeJSON[keyJSON]):
        if keyJSON in anonymizedKeys or listAnonymize:
            nodeJSON[keyJSON] = ''.join(random.choice(string.digits) for _ in range(4))
    else:
        eprintf("ERROR: Unknown value type")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Anonymize Bluemix conversation service dialog in json format.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('dialog', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='file with dialog in .json format, if not specified, dialog is read from standard input')
    args = parser.parse_args(sys.argv[1:])

    # load dialog JSON
    dialogJSON = json.load(args.dialog)

    anonymize(dialogJSON, "dialog_nodes")

    stringJSON = json.dumps(dialogJSON, indent=4)
    # replace intent names
    stringJSON = re.sub("#[a-zA-Z_-]*", '#' + ''.join(random.choice(string.ascii_uppercase) for _ in range(10)), stringJSON)
    # replace entities
    stringJSON = re.sub("@[a-zA-Z_-]*", '@' + ''.join(random.choice(string.ascii_lowercase) for _ in range(5)), stringJSON)
    # replace entity values
    stringJSON = re.sub("@[a-zA-Z_-]*:[a-zA-Z_-]*", '@' + ''.join(random.choice(string.ascii_lowercase) for _ in range(5)) + ':' + ''.join(random.choice(string.ascii_lowercase) for _ in range(8)), stringJSON)
    # replace quotated strings
    stringJSON = re.sub("\'[a-zA-Z0-9_\-]*\'", "'" + ''.join(random.choice(string.ascii_lowercase) for _ in range(8)) + "'", stringJSON)
    # replace links
    stringJSON = re.sub("https*://[a-zA-Z0-9_\-\./]*", "https://" + ''.join(random.choice(string.ascii_lowercase) for _ in range(30)) + ".com", stringJSON)


    # replace specific texts
    for stringToReplace in anonymizedStrings1:
        stringJSON = re.sub(stringToReplace, ''.join(random.choice(string.ascii_lowercase) for _ in range(8)), stringJSON)
    # replace specific texts
    for stringToReplace in anonymizedStrings3:
        stringJSON = re.sub(stringToReplace, ''.join(random.choice(string.ascii_lowercase) for _ in range(8)), stringJSON)

    print(stringJSON)
