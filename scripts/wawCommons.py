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

import sys, re, codecs, os, fnmatch
import unicodedata, unidecode, requests
import lxml.etree as Xml
import logging
from logging.config import fileConfig


restrictionTextNamePolicy = "NAME_POLICY can be only set to either 'soft', 'soft_verbose' or 'hard'"

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
            logger.warning("Illegal value of the code: '%s'- %s", code, restrictionTextCode)
            logger.warning("Code \'%s\' changed to: '%s'", code, newCode)
        elif NAME_POLICY == 'hard':
            logger.error("Illegal value of the code: '%s' - %s", code, restrictionTextCode)
            exit(1)
        elif NAME_POLICY != 'soft':
            logger.error("Unknown value of the NAME_POLICY: '%s' - %s", NAME_POLICY, restrictionTextNamePolicy)
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
                        logger.error("unsupported special regex opperation '" + replacementPair[1].decode('utf-8'))
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
                #logger.warning("Illegal value of the intent name: '%s'- %s", uIntentSubname, ' '.join(restrictionTextIntentName).decode('utf-8'))
                #logger.warning("Intent name \'%s\' changed to: '%s'", uIntentSubname, uIntentSubnameUser)
            elif NAME_POLICY == 'hard':
                logger.error("Illegal value of the intent name: '%s' - %s", uIntentSubname, ' '.join(restrictionTextIntentName).decode('utf-8'))
                exit(1)
            else:
                logger.error("Unknown value of the NAME_POLICY: '%s' - %s", NAME_POLICY, restrictionTextNamePolicy)
                exit(1)

        #uIntentSubnameNoHash = uIntentSubname[1:] if uIntentSubname.startswith(u'#') else uIntentSubname
        uIntentSubnameNoHash = uIntentSubnameUser[1:] if uIntentSubnameUser.startswith(u'#') else uIntentSubname

        # if uIntentSubnameUser != uIntentSubnameNoHash:
        #     if NAME_POLICY == 'soft_verbose':
        #         logger.warning("Illegal value of the intent name: '%s' - %s", uIntentSubname, ' '.join(restrictionTextIntentName).decode('utf-8'))
        #         logger.warning("Intent name \'%s\' changed to: '%s'", uIntentSubname, uIntentSubnameUser)
        #     elif NAME_POLICY == 'hard':
        #         logger.error("Illegal value of the intent name: '%s' - %s", uIntentSubname, ' '.join(restrictionTextIntentName).decode('utf-8'))
        #         exit(1)
        #     elif NAME_POLICY == 'soft':
        #         exit(1)
        #     else:
        #         logger.error("Unknown value of the NAME_POLICY: '%s' - %s", NAME_POLICY, restrictionTextNamePolicy)
        #         exit(1)
        if not uIntentSubnameUser:
            logger.error("empty intent name")
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
                    logger.error("unsupported special regex opperation '" + replacementPair[1].decode('utf-8'))
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
            logger.warning("Illegal value of the entity name: '%s' - %s", uEntityName, " ".join(restrictionTextEntityName).decode('utf-8'))
            logger.warning("Entity name \'%s\' was changed to: '%s'", uEntityName, uEntityNameUser)
        elif NAME_POLICY == 'hard':
            logger.error("Illegal value of the entity name: '%s' - %s", uEntityName, " ".join(restrictionTextEntityName).decode('utf-8'))
            exit(1)
        else:
            logger.error("Unknown value of the NAME_POLICY: '%s' - %s", NAME_POLICY, restrictionTextNamePolicy)
            exit(1)
    if not uEntityNameUser:
        logger.error("empty entity name")
        exit(1)
    return uEntityNameUser.encode('utf-8')

def getFilesAtPath(pathList, patterns=['*']):
    """
    Obtains list of absolute file paths (while filenames are filtered by patterns) that are present in specified paths.

    This function processes paths supplied in first parameters. If the path is regular file then this file is addded
    to output list if matches one of supplied patterns. If path is directory then all files from this directory
    (even the files contained in subdirectories) are taken (but for every file is checked if it matches one of
    supplied patterns). Note that the patterns are applied on the filenames only!

    Parameters
    ----------
    pathList : list
        List of paths that will be searched (each item can be either regular file or directory)
    patterns : list
        List of file patterns, each file name in output list must match at least to one these pattern;
        i.e. this pattern list behaves like there is OR operator between patterns;
        patterns format is described here https://docs.python.org/2.7/library/fnmatch.html

    Returns
    -------
    list
        List of file paths (in absolute form) found in specified paths and matching to specified patterns
    """
    filesAtPath = []
    for pathItem in pathList:
        # is it a directory? - take all files in it (if they match one of the patterns)
        if os.path.isdir(pathItem):
            filesAtPath.extend(absoluteFilePaths(pathItem, patterns))
        # is it a file? - take it (if it matches one of the patterns)
        elif os.path.exists(pathItem):
            if _fileMatchesPatterns(os.path.basename(pathItem), patterns):
                filesAtPath.append(os.path.abspath(pathItem))
        # is it NONE? - ignore it
        else:
            pass
    return filesAtPath

def absoluteFilePaths(directory, patterns=['*']):
    """
    Returns generator which yields all files in specified directory (and subdirectories) that match
    one of the patterns.
    """
    for dirpath,_,filenames in os.walk(directory):
        for f in filenames:
            if _fileMatchesPatterns(f, patterns):
                yield os.path.abspath(os.path.join(dirpath, f))

def _fileMatchesPatterns(filename, patterns):
    """Helper function which checks if file matches one the patterns."""
    for pattern in patterns:
        if fnmatch.fnmatchcase(filename, pattern):
            return True
    return False

def getWorkspaceId(config, workspacesUrl, version, username, password):

    workspaceId = getOptionalParameter(config, 'conversation_workspace_id')

    if not workspaceId:
        workspaceId = ""

        # workspace name is considered as unique
        workspaceNameUnique = getOptionalParameter(config, 'conversation_workspace_name_unique')
        if workspaceNameUnique in ["true", "True"]:
            logger.info('conversation_workspace_name set to unique')

            workspaceName = getOptionalParameter(config, 'conversation_workspace_name')
            if workspaceName:
                # get all workspaces with this name
                requestUrl = workspacesUrl + '?version=' + version
                logger.info("request url: %s", requestUrl)
                response = requests.get(workspacesUrl + '?version=' + version, auth=(username, password))
                responseJson = response.json()
                logger.info("response: %s", responseJson)
                if not errorsInResponse(responseJson):
                    logger.info('Workspaces successfully retrieved.')
                else:
                    logger.error('Cannot retrieve workspaces.')
                    sys.exit(1)

                sameNameWorkspace = None
                for workspace in responseJson['workspaces']:
                    logger.info("workspace name: " + workspace['name'])
                    if workspace['name'] == workspaceName:
                        if sameNameWorkspace is None:
                            sameNameWorkspace = workspace
                        else:
                            # if there is more than one workspace with the same name -> error
                            logger.error('There are more than one workspace with this name, do not know which one to update.')
                            exit(1)
                if sameNameWorkspace is None:
                    # workspace with the same name not found
                    logger.warning('There is no workspace with this name.')
                else:
                    # just one workspace with this name -> get its id
                    workspaceId = sameNameWorkspace['workspace_id']

            else: # workspace name unique and not defined or empty
                logger.error("'conversation_workspace_name' set to unique but not defined.")
                exit(1)

        else: # workspace name not unique
            logger.info("Workspace name doesn't have to be unique")

    return workspaceId

def errorsInResponse(responseJson):
    # check errors
    if 'error' in responseJson:
        logger.error('%s (code %s)', responseJson['error'], responseJson['code'])
        if 'errors' in responseJson:
            for errorJson in responseJson['errors']:
                logger.error('\t path: \'%s\' - %s', errorJson['path'], errorJson['message'])
#        if VERBOSE: logger.error("WORKSPACE: %s", json.dumps(workspace, indent=4))
        return True
    else:
        return False

def getOptionalParameter(config, parameterName):
    if hasattr(config, parameterName) and getattr(config, parameterName):
        parameterValue = getattr(config, parameterName)
        return parameterValue
    else:
        logger.warning("'%s' parameter not defined", parameterName)
        return None

def getRequiredParameter(config, parameterName):
    if hasattr(config, parameterName) and getattr(config, parameterName):
        parameterValue = getattr(config, parameterName)
        return parameterValue
    else:
        logger.error("required '%s' parameter not defined", parameterName)
        exit(1)

def setLoggerConfig():
    fileConfig(os.path.split(os.path.abspath(__file__))[0]+'/logging_config.ini')

def getScriptLogger(script):
    return logging.getLogger("common."+os.path.splitext(os.path.basename(script))[0])

logger = getScriptLogger(__file__)
