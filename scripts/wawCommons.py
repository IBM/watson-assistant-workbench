# -*- coding: utf-8 -*-

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

import sys, re, codecs, os
import unicodedata, unidecode
import lxml.etree as Xml

restrictionTextNamePolicy = "NAME_POLICY can be only set to either 'soft', 'soft_verbose' or 'hard'"

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

def printf(format, *args):
    sys.stdout.write(format % args)
    sys.stdout.flush()

def eprintf(format, *args):
    sys.stderr.write(format % args)
    sys.stderr.flush()

def toCode(NAME_POLICY, code):
    global restrictionTextNamePolicy
    restrictionTextCode = "The code can only contain uppercase letters (in Unicode), numbers, underscores, and hyphens."
    code = code.strip()
    newCode = re.sub(' ', '_', code, re.UNICODE).upper()
    if isinstance(newCode, str):
        newIntentSubname = newCode.decode('utf-8')
        # use unidecode.unidecode ?
        newCode = unicodedata.normalize('NFKD', newCode.decode('utf-8')).encode('ASCII', 'ignore')  # remove accents
    # remove everything that is not unicode letter or hyphen
    newCode = re.sub('[^\w-]', '', newCode, re.UNICODE)
    if newCode != code:
        if NAME_POLICY == 'soft_verbose':
            eprintf("WARNING: Illegal value of the code: '%s'\n%s\n", code, restrictionTextCode)
            eprintf("WARNING: Code \'%s\' changed to: '%s'\n", code, newCode)
        elif NAME_POLICY == 'hard':
            eprintf("ERROR: Illegal value of the code: '%s'\n%s\n", code, restrictionTextCode)
            exit(1)
        elif NAME_POLICY != 'soft':
            eprintf("ERROR: Unknown value of the NAME_POLICY: '%s'\n%s\n", NAME_POLICY, restrictionTextNamePolicy)
            exit(1)
    return newCode

def normalizeIntentName(intentName):
    """Normalizes intent name to uppercase, with no dashes or underscores"""
    return re.sub('[-_]', '', intentName).upper()

def toIntentName(NAME_POLICY, userReplacements, *intentSubnames):
    """Concatenates intent names with underscores,
    checks if the intent name satisfies all restrictions given by WA and user.
    WA replacements:
     - replace spaces and semicolons with uderscores
     - remove everything that is not unicode letter, hyphen or period
    User defined replacements:
     e.g. userReplacements = [['$special', '\L'], ['-', '_']] which change all letters to lowercase and replace all hyphens for underscores
    If the name does not satisfy all restrictions, this function will return corrected name and print warning (NAME_POLICY soft_verbose)
    or it will end up with an error (NAME_POLICY hard)"""
    """Removes all unexpected characters from the intent names, normalize them to upper case and concatenate them with the underscores"""
    global restrictionTextNamePolicy
    restrictionTextIntentName = []
    uNewIntentName = u""
    for intentSubname in intentSubnames:
        if not intentSubname: continue
        intentSubname = intentSubname.strip()
        uIntentSubname = intentSubname.decode('utf-8') if isinstance(intentSubname, str) else intentSubname
        # apply WA restrictions (https://console.bluemix.net/docs/services/conversation/intents.html#defining-intents)
        uIntentSubnameWA = re.sub(' ;', '_', uIntentSubname, re.UNICODE) # replace space and ; by underscore
        uIntentSubnameWA = re.sub(u'[^\wÀ-ÖØ-öø-ÿĀ-ž-\.]', '', uIntentSubnameWA, re.UNICODE) # remove everything that is not unicode letter, hyphen or period
        if uIntentSubnameWA != uIntentSubname: # WA restriction triggered
            restrictionTextIntentName.append("The intent name can only contain letters (in Unicode), numbers, underscores, hyphens, and periods.")
        # apply user-defined restrictions
        uIntentSubnameUser = uIntentSubnameWA
        if userReplacements:
            triggeredUserRegex = []
            # re.sub for all pairs (regex, replacement)
            for replacementPair in userReplacements:
                #special case
                if replacementPair[0].startswith('$'):
                    if replacementPair[1] == r'\L':
                        uNewIntentSubnameUser = uIntentSubnameUser.lower()
                        triggeredUserRegexToAppend = "intent name should be lowercase"
                    elif replacementPair[1] == r'\U':
                        uNewIntentSubnameUser = uIntentSubnameUser.upper()
                        triggeredUserRegexToAppend = "intent name should be uppercase"
                    elif replacementPair[1] == r'\A':
                        uNewIntentSubnameUser = unidecode.unidecode(uIntentSubnameUser)
                        triggeredUserRegexToAppend = "intent name cannot contain accented letters"
                    else:
                        eprintf("ERROR: unsupported special regex opperation '" + replacementPair[1].decode('utf-8') + "'\n")
                        exit(1)
                # use regex
                else:
                    uNewIntentSubnameUser = re.sub(replacementPair[0].decode('utf-8'), replacementPair[1].decode('utf-8'), uIntentSubnameUser, re.UNICODE)
                    triggeredUserRegexToAppend = replacementPair[0] + "' should be replaced with '" + replacementPair[1]
                # this replacement pair triggered
                if uNewIntentSubnameUser != uIntentSubnameUser:
                    triggeredUserRegex.append(triggeredUserRegexToAppend)
                uIntentSubnameUser = uNewIntentSubnameUser
            if uIntentSubnameUser != uIntentSubnameWA: # user restriction triggered
                restrictionTextIntentName.append("User-defined regex: '" + "', '".join(triggeredUserRegex) + "'.")

        if uIntentSubnameUser != uIntentSubname:
            if NAME_POLICY == 'soft':
                uIntentSubnameUser=uIntentSubnameUser; #TBD- delete this when logging is fixed
                #eprintf("WARNING: Illegal value of the intent name: '%s'\n%s\n", uIntentSubname, ' '.join(restrictionTextIntentName).decode('utf-8'))
                #eprintf("WARNING: Intent name \'%s\' changed to: '%s'\n", uIntentSubname, uIntentSubnameUser)
            elif NAME_POLICY == 'hard':
                eprintf("ERROR: Illegal value of the intent name: '%s'\n%s\n", uIntentSubname, ' '.join(restrictionTextIntentName).decode('utf-8'))
                exit(1)
            else:
                eprintf("ERROR: Unknown value of the NAME_POLICY: '%s'\n%s\n", NAME_POLICY, restrictionTextNamePolicy)
                exit(1)

        #uIntentSubnameNoHash = uIntentSubname[1:] if uIntentSubname.startswith(u'#') else uIntentSubname
        uIntentSubnameNoHash = uIntentSubnameUser[1:] if uIntentSubnameUser.startswith(u'#') else uIntentSubname

        # if uIntentSubnameUser != uIntentSubnameNoHash:
        #     if NAME_POLICY == 'soft_verbose':
        #         eprintf("WARNING: Illegal value of the intent name: '%s'\n%s\n", uIntentSubname, ' '.join(restrictionTextIntentName).decode('utf-8'))
        #         eprintf("WARNING: Intent name \'%s\' changed to: '%s'\n", uIntentSubname, uIntentSubnameUser)
        #     elif NAME_POLICY == 'hard':
        #         eprintf("ERROR: Illegal value of the intent name: '%s'\n%s\n", uIntentSubname, ' '.join(restrictionTextIntentName).decode('utf-8'))
        #         exit(1)
        #     elif NAME_POLICY == 'soft':
        #         exit(1)
        #     else:
        #         eprintf("ERROR: Unknown value of the NAME_POLICY: '%s'\n%s\n", NAME_POLICY, restrictionTextNamePolicy)
        #         exit(1)
        if not uIntentSubnameUser:
            eprintf("ERROR: empty intent name\n")
            exit(1)
        uNewIntentName = uNewIntentName + u'_' + uIntentSubnameUser if uNewIntentName else uIntentSubnameUser
    return uNewIntentName.encode('utf-8')

def toEntityName(NAME_POLICY, userReplacements, entityName):
    """Checks if the entity name satisfies all restrictions given by WA and user.
    WA replacements:
     - replace spaces with uderscores
     - remove everything that is not unicode letter or hyphen
    User defined replacements:
     e.g. userReplacements = [['$special', '\L'], ['-', '_']] which change all letters to lowercase and replace all hyphens for underscores
    If the name does not satisfy all restrictions, this function will return corrected name and print warning (NAME_POLICY soft)
    or it will end up with an error (NAME_POLICY hard)"""
    global restrictionTextNamePolicy
    restrictionTextEntityName = []
    entityName = entityName.strip()
    uEntityName = entityName.decode('utf-8') if isinstance(entityName, str) else entityName
    # apply WA restrictions (https://console.bluemix.net/docs/services/conversation/entities.html#defining-entities)
    uEntityNameWA = re.sub(' ', '_', uEntityName, re.UNICODE) # replace spaces with underscores
    uEntityNameWA = re.sub(u'[^\wÀ-ÖØ-öø-ÿĀ-ž-]', '', uEntityNameWA, re.UNICODE) # remove everything that is not unicode letter or hyphen
    if uEntityNameWA != uEntityName: # WA restriction triggered
        restrictionTextEntityName.append("The entity name can only contain letters (in Unicode), numbers, underscores, and hyphens.")
    # apply user-defined restrictions
    uEntityNameUser = uEntityNameWA
    if userReplacements:
        triggeredUserRegex = []
        # re.sub for all pairs (regex, replacement)
        for replacementPair in userReplacements:
            #special case
            if replacementPair[0].startswith('$'):
                if replacementPair[1] == r'\L':
                    uNewEntityNameUser = uEntityNameUser.lower()
                    triggeredUserRegexToAppend = "entity name should be lowercase"
                elif replacementPair[1] == r'\U':
                    uNewEntityNameUser = uEntityNameUser.upper()
                    triggeredUserRegexToAppend = "entity name should be uppercase"
                elif replacementPair[1] == r'\A':
                    uNewIntentSubnameUser = unidecode.unidecode(uEntityNameUser)
                    triggeredUserRegexToAppend = "entity name cannot contain accented letters"
                else:
                    eprintf("ERROR: unsupported special regex opperation '" + replacementPair[1].decode('utf-8') + "'\n")
                    exit(1)
            # use regex
            else:
                uNewEntityNameUser = re.sub(replacementPair[0].decode('utf-8'), replacementPair[1].decode('utf-8'), uEntityNameUser, re.UNICODE)
                triggeredUserRegexToAppend = replacementPair[0] + "' should be replaced with '" + replacementPair[1]
            # this replacement pair triggered
            if uNewEntityNameUser != uEntityNameUser:
                triggeredUserRegex.append(triggeredUserRegexToAppend)
            uEntityNameUser = uNewEntityNameUser
        if uEntityNameUser != uEntityNameWA: # user restriction triggered
            restrictionTextEntityName.append("User-defined regex: '" + "', '".join(triggeredUserRegex) + "'.")
    # return error or name
    if uEntityNameUser != uEntityName: # allowed name differs from the given one
        if NAME_POLICY == 'soft':
            eprintf("WARNING: Illegal value of the entity name: '%s'\n%s\n", uEntityName, " ".join(restrictionTextEntityName).decode('utf-8'))
            eprintf("WARNING: Entity name \'%s\' was changed to: '%s'\n", uEntityName, uEntityNameUser)
        elif NAME_POLICY == 'hard':
            eprintf("ERROR: Illegal value of the entity name: '%s'\n%s\n", uEntityName, " ".join(restrictionTextEntityName).decode('utf-8'))
            exit(1)
        else:
            eprintf("ERROR: Unknown value of the NAME_POLICY: '%s'\n%s\n", NAME_POLICY, restrictionTextNamePolicy)
            exit(1)
    if not uEntityNameUser:
        eprintf("ERROR: empty entity name\n")
        exit(1)
    return uEntityNameUser.encode('utf-8')

def getFilesAtPath(pathList):
    filesAtPath = []
    for pathItem in pathList:
        # is it a directory? - take all files in it
        if os.path.isdir(pathItem):
            filesAtPath.extend(absoluteFilePaths(pathItem))
        # is it a file? - take it
        elif os.path.exists(pathItem):
            filesAtPath.append(os.path.abspath(pathItem))
        # is it NONE? - ignore it
        else:
            pass
    return filesAtPath

def absoluteFilePaths(directory):
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))
