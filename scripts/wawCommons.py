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

import copy, sys, re, codecs, os, io, unidecode, types, fnmatch, requests, json
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import lxml.etree as Xml
import logging
from logging.config import fileConfig


def openFile(name, *args, **kwargs):
    if 'encoding' not in kwargs.keys():
        kwargs['encoding'] = 'utf-8'
    f = io.open(name,*args, **kwargs)
    return f

restrictionTextNamePolicy = "NAME_POLICY can be only set to either 'soft', 'soft_verbose' or 'hard'"

def toCode(NAME_POLICY, code):
    global restrictionTextNamePolicy
    restrictionTextCode = "The code can only contain uppercase letters (in Unicode), numbers, underscores, and hyphens."
    code = code.strip()
    newCode = re.sub(' ', '_', code, re.UNICODE).upper()
    newCode = unidecode.unidecode(newCode) #unicodedata.normalize('NFKD', newCode.decode('utf-8')).encode('ASCII', 'ignore')  # remove accents
    # remove everything that is not unicode letter or hyphen
    newCode = re.sub('[^\\w-]', '', newCode, re.UNICODE)
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


#TODO uncomplicate
def toIntentName(NAME_POLICY, userReplacements, *intentSubnames):
    """Concatenates intent names with underscores,
    checks if the intent name satisfies all restrictions given by WA and user.
    WA replacements:
     - replace spaces and semicolons with uderscores
     - remove everything that is not unicode letter, hyphen or period
    User defined replacements:
     e.g. userReplacements = [['$special', '\\L'], ['-', '_']] which change all letters to lowercase and replace all hyphens for underscores
    If the name does not satisfy all restrictions, this function will return corrected name and print warning (NAME_POLICY soft_verbose)
    or it will end up with an error (NAME_POLICY hard)"""
    """Removes all unexpected characters from the intent names, normalize them to upper case and concatenate them with the underscores"""
    global restrictionTextNamePolicy
    restrictionTextIntentName = []
    uNewIntentName = u""
    for intentSubname in intentSubnames:
        if not intentSubname: continue
        intentSubname = intentSubname.strip()
        uIntentSubname = intentSubname
        # apply WA restrictions (https://console.bluemix.net/docs/services/conversation/intents.html#defining-intents)
        uIntentSubnameWA = re.sub(' ;', '_', uIntentSubname, re.UNICODE) # replace space and ; by underscore
        uIntentSubnameWA = re.sub(u'[^\\wÀ-ÖØ-öø-ÿĀ-ž-\\.]', '', uIntentSubnameWA, re.UNICODE) # remove everything that is not unicode letter, hyphen or period
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
                    uNewIntentSubnameUser = re.sub(replacementPair[0], replacementPair[1], uIntentSubnameUser, re.UNICODE)
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
    return uNewIntentName
# TODO uncomplicate
def toEntityName(NAME_POLICY, userReplacements, entityName):
    """Checks if the entity name satisfies all restrictions given by WA and user.
    WA replacements:
     - replace spaces with uderscores
     - remove everything that is not unicode letter or hyphen
    User defined replacements:
     e.g. userReplacements = [['$special', '\\L'], ['-', '_']] which change all letters to lowercase and replace all hyphens for underscores
    If the name does not satisfy all restrictions, this function will return corrected name and print warning (NAME_POLICY soft)
    or it will end up with an error (NAME_POLICY hard)"""
    global restrictionTextNamePolicy
    restrictionTextEntityName = []
    entityName = entityName.strip()
    uEntityName = entityName
    # apply WA restrictions (https://console.bluemix.net/docs/services/conversation/entities.html#defining-entities)
    uEntityNameWA = re.sub(' ', '_', uEntityName, re.UNICODE) # replace spaces with underscores
    uEntityNameWA = re.sub(u'[^\\wÀ-ÖØ-öø-ÿĀ-ž-]', '', uEntityNameWA, re.UNICODE) # remove everything that is not unicode letter or hyphen
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
                uNewEntityNameUser = re.sub(replacementPair[0], replacementPair[1], uEntityNameUser, re.UNICODE)
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
    return uEntityNameUser

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
    """Helper function which checks if file matches one of the patterns."""
    for pattern in patterns:
        if fnmatch.fnmatchcase(filename, pattern):
            return True
    return False

def getWorkspaces(workspacesUrl, version, username, password):
    """
    Returns a list of all workspaces that match given criteria.
    """

    # get all workspaces
    requestUrl = workspacesUrl + '?version=' + version
    logger.info("request url: %s", requestUrl)
    response = requests.get(requestUrl, auth=(username, password))
    responseJson = response.json()
    logger.debug("response: %s", responseJson)
    if not errorsInResponse(responseJson):
        logger.info('Workspaces successfully retrieved.')
    else:
        logger.error('Cannot retrieve workspaces.')
        sys.exit(1)

    if 'workspaces' in responseJson:
        return responseJson['workspaces']
    else:
        logger.error('No workspaces key in the response')
        sys.exit(1)

def filterWorkspaces(config, workspaces):

    matchingWorkspaces = []

    matchByName = getOptionalParameter(config, 'conversation_workspace_match_by_name')
    # workspace is matched by name (or pattern if defined)
    if matchByName in ["true", "True"]:
        logger.info("workspace is matched by 'conversation_workspace_name' (or by 'conversation_workspace_name_pattern' if defined)")
        workspaceNamePattern = getOptionalParameter(config, 'conversation_workspace_name_pattern')
        if workspaceNamePattern is None:
            workspaceNamePattern = getOptionalParameter(config, 'conversation_workspace_name')
        if workspaceNamePattern:
            pattern = re.compile(workspaceNamePattern)

            for workspace in workspaces:
                logger.debug("workspace name: " + workspace['name'])
                if pattern.match(workspace['name']):
                    matchingWorkspaces.append(workspace)
                    logger.info("workspace name match: " + workspace['name'])

        else: # workspace match by name and name nor pattenot defined or empty
            logger.critical("'conversation_workspace_match_by_name' set to true but neither 'conversation_workspace_name' nor 'conversation_workspace_name_pattern' is defined.")
            sys.exit(1)

    else: # workspace matched by id (default option)
        logger.info("workspace is matched by 'conversation_workspace_id'")
        workspaceId = getOptionalParameter(config, 'conversation_workspace_id')
        if workspaceId:

            for workspace in workspaces:
                logger.debug("workspace name: " + workspace['name'])
                if workspaceId == workspace['workspace_id']:
                    matchingWorkspaces.append(workspace)
                    logger.info("workspace name match: " + workspace['name'])

        else: # returns empty list
            logger.warning("workspace is matched by 'conversation_workspace_id' but no id specified")

    return matchingWorkspaces

def filterPackages(config, packages):
    matchingPackages = []
    packageNamePattern = getOptionalParameter(config, 'cloudfunctions_package_pattern')

    if packageNamePattern is None:
        packageNamePattern = getOptionalParameter(config, 'cloudfunctions_package')
    if packageNamePattern:
        pattern = re.compile(packageNamePattern)

        for package in packages:
            logger.debug("package name: " + package['name'])
            if pattern.match(package['name']):
                matchingPackages.append(package)
                logger.info("package name match: " + package['name'])

    else:
        logger.critical("neither 'cloudfunctions_package' nor 'cloudfunctions_package_pattern' is defined.")
        sys.exit(1)

    return matchingPackages

def errorsInResponse(responseJson):
    # check errors
    if 'error' in responseJson:
        logger.error('Error in response: %s (WA code %s)', responseJson['error'], responseJson['code'])
        if 'errors' in responseJson:
            for errorJson in responseJson['errors']:
                logger.error('\t path: \'%s\' - %s', errorJson['path'], errorJson['message'])
#       logger.verbose("WORKSPACE: %s", json.dumps(workspace, indent=4))
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

def getParametersCombination(config, *args):
    """
    Obtains list of arguments where each argument represents one combination of parameters
    that should be retrived from configuration file. Only one combination of arguments could
    be set in configuration file (between parameters in combination there is logical AND,
    between combinations there is XOR - only one can be set).

    Parameters
    ----------
    config : Cfg
        Configuration to be used for searching of parameters
    args : (string | list)*
        Each argument could be parameter name or list of parameters names

    Returns
    -------
    dict
        Parameters combination with values
    """
    parametersCombinationMap = {}

    if not config:
        logger.critical("config is null")
        exit(1)

    if len(args) == 0:
        logger.critical("no parameters combination provided to be retrieved")
        exit(1)

    for arg in args:
        if isinstance(arg, str):
            if getattr(config, arg, None):
                if parametersCombinationMap:
                    logger.critical("only one combination of parameters can be set, " +
                        "combination already set: '%s', " +
                        "another argument set: '%s'", str(sorted(list(parametersCombinationMap))), arg)
                    exit(1)
                parametersCombinationMap[arg] = getattr(config, arg)
        elif isinstance(arg, list):
            parametersCombinationMapCurrent = {}
            parametersCombinationMissing = []
            for parameterName in arg:
                if getattr(config, parameterName, None):
                    if parametersCombinationMap:
                        logger.critical("only one combination of parameters can be set, " +
                            "combination already set: '%s', " +
                            "another argument set: '%s'", str(sorted(list(parametersCombinationMap))), parameterName)
                        exit(1)
                    parametersCombinationMapCurrent[parameterName] = getattr(config, parameterName)
                else:
                    parametersCombinationMissing.append(parameterName)
            if parametersCombinationMapCurrent:
                if len(parametersCombinationMapCurrent) != len(arg):
                    logger.critical("part of parameters combination is set, but some params are missing, " +
                        "combination: '%s', " +
                        "missing parameters: '%s'", str(arg), str(parametersCombinationMissing))
                    exit(1)
                parametersCombinationMap = parametersCombinationMapCurrent
        else:
            logger.critical("arguments could be only parameter names or array of parameters names, arg type '%s'", str(type(arg).__name__))
            exit(1)

    if not parametersCombinationMap:
        logger.critical("no parameters combination is set in configuration, " +
            "you have to provide exactly one of those combinations of parameters:'")
        for index, arg in enumerate(args):
            logger.critical("Combination %d: \'%s\'", index, str(arg))
        exit(1)

    return parametersCombinationMap

def setLoggerConfig(level=None, isVerbose=False, configPath=None):
    d = os.path.dirname(os.path.abspath(__file__))
    fileConfig(configPath or d+'/logging_config.ini')
    l = logging.getLogger()
    logging.Logger.isVerbose = isVerbose

    def verbose(self, message, *args, **kws):
        if (logging.Logger.isVerbose):
            self.info(message, *args, **kws)

    logging.Logger.verbose = verbose
    if level:
        levelName = logging.getLevelName(level)
        l.setLevel(levelName)
        for h in l.handlers:
            h.setLevel(levelName)

def getScriptLogger(script):
    return logging.getLogger("common."+os.path.splitext(os.path.basename(script))[0])

def convertApikeyToUsernameAndPassword(apikey):
    """
    Obtains 'apikey' string that is in format \'username:password\' and returns
    tuple (username, password).

    Parameters
    ----------
    apikey : string
        Apikey in format \'username:password\'

    Returns
    -------
    tuple : (username, password)
        Username and password parsed from 'apikey'
    """
    if isinstance(apikey, str):
        apikeySplit = apikey.split(':')
        if len(apikeySplit) == 2:
            return (apikeySplit[0], apikeySplit[1])
    logger.critical('Apikey has invalid format (valid format is string: \'username:password\')')
    sys.exit(1)

def replaceValue(sourceJson, target, replacementJson, matchKey = True):
    """
    Finds recursively 'target' in 'sourceJson' object and replaces its value by 'replacementJson'.
    Based on given parameter 'matchKey', function tries to find key or value as a 'target'
    (if 'matchKey' == True then it tries to find key as a 'target'). It returnes number
    of replacements and modified json (sourceJson is not changed).

    Parameters
    ----------
    sourceJson : object
    target : string
    replacementJson : object
    matchKey: boolean

    Returns
    -------
    tuple : (targetJson, replacedValuesNumber)
        Number of replacements and modified json.
    """
    replacedValuesNumber = 0
    targetJson = copy.deepcopy(sourceJson)
    if sourceJson and target:
        if isinstance(sourceJson, list):
            for index, item in enumerate(sourceJson):
                rJson, rValuesNumber = replaceValue(item, target, replacementJson, matchKey)
                replacedValuesNumber += rValuesNumber
                targetJson[index] = rJson
        elif isinstance(sourceJson, dict):
            for key in sourceJson:
                if matchKey and key == target:
                    targetJson[key] = copy.deepcopy(replacementJson)
                    replacedValuesNumber += 1
                else:
                    rJson, rValuesNumber = replaceValue(sourceJson[key], target, replacementJson, matchKey)
                    replacedValuesNumber += rValuesNumber
                    targetJson[key] = rJson
        elif not matchKey and sourceJson == target:
            targetJson = copy.deepcopy(replacementJson)
            replacedValuesNumber += 1
    return targetJson, replacedValuesNumber

def getFunctionResponseJson(cloudFunctionsUrl, urlNamespace, username, password, package, functionName, parameters, data):

    functionUrl = cloudFunctionsUrl + '/' + urlNamespace + '/actions/' + package + '/' + functionName
    url_parts = list(urlparse(functionUrl))
    params = {'blocking':True, 'result': True} # wait for result and return only result
    params.update(parameters) # add custom parameters
    url_parts[4] = urlencode(params)
    functionCallUrl = urlunparse(url_parts)

    logger.info("Calling function url '%s'", functionCallUrl)

    functionResponse = requests.post(functionCallUrl, auth=(username, password),
                                 headers={'Content-Type': 'application/json',
                                          'accept': 'application/json'},
                                 data=json.dumps(data, ensure_ascii=False).encode('utf8'))

    if functionResponse.status_code == 200:

        responseContentType = functionResponse.headers.get('content-type')
        if responseContentType != 'application/json':
            logger.error('Response content type is not json, content type: %s, response:\n%s', responseContentType, functionResponse.text)
            return None

        return functionResponse.json()

    elif functionResponse.status_code == 202: # try once more
        # 202 Accepted activation request (should not happen while sending 'blocking=true&result=true')
        logger.warning("Did not receive response from function '%s' in package '%s', trying once more.", functionName, package)
        logger.info(json.dumps(functionResponse.json()))
        responseJson = functionResponse.json()
        activationId = responseJson['activationId']
        functionCallUrl = cloudFunctionsUrl + '/' + urlNamespace + '/activations/' + activationId + '/result'
        logger.info("Trying to get function result from url '%s'", functionCallUrl)
        functionResponse = requests.get(functionCallUrl, auth=(username, password),
                                        headers={})
        if functionResponse.status_code == 200:

            responseContentType = functionResponse.headers.get('content-type')
            if responseContentType != 'application/json':
                logger.error('Response content type is not json, content type: %s, response:\n%s', responseContentType, functionResponse.text)
                return None

            responseJson = functionResponse.json()
            if isinstance(responseJson, dict) and 'result' in responseJson\
             and isinstance(responseJson['result'], dict) and 'payload' in responseJson['result']:
                return responseJson['result']['payload']
            else:
                logger.error("Bad response format received from function '%s' in package '%s', status code '%d',\
                 response: %s, expected was {\"result\":{\"payload\":\"<function_payload>\"}}",\
                 functionName, package, functionResponse.status_code, json.dumps(functionResponse.json(), ensure_ascii=False).encode('utf8'))
                return None

        elif functionResponse.status_code in [403, 404, 408]: # not so serious errors, the next request may be fine
            # 403 Forbidden (could be just for specific package or function)
            # 404 Not Found (action or package could be incorrectly specified for given request)
            # 408 Request Timeout (could happen e.g. for CF that requests some REST APIs, e.g. Discovery service)
            logger.error("Unexpected response status from function '%s' in package '%s' with activation id '%s', status code '%d', response: %s",
                         functionName, package, activationId, functionResponse.status_code,
                         functionResponse.text)
            return None
        else: # serious errors, stop the process
            # 401 Unauthorized (while we use same credentials for all tests then we want to end after the first test returns bad authentification)
            # 500 Internal Server Error (could happen that IBM Cloud has several issue and is not able to handle incoming requests,
             # then it would be probably same for all requests)
            # 502 Bad Gateway (when the CF raises exception, e.g. bad params were provided)
            logger.critical("Unexpected response status from function '%s' in package '%s' with activation id '%s', status code '%d', response: %s",
                            functionName, package, activationId, functionResponse.status_code, functionResponse.text)
            sys.exit(1)

    elif functionResponse.status_code in [403, 404, 408]: # not so serious errors, the next request may be fine
        # 403 Forbidden (could be just for specific package or function)
        # 404 Not Found (action or package could be incorrectly specified for given request)
        # 408 Request Timeout (could happen e.g. for CF that requests some REST APIs, e.g. Discovery service)
        logger.error("Unexpected response status from function '%s' in package '%s', status code '%d', response: %s",
                     functionName, package, functionResponse.status_code,
                     functionResponse.text)
    else: # serious errors, stop the process
        # 401 Unauthorized (while we use same credentials for all tests then we want to end after the first test returns bad authentification)
        # 500 Internal Server Error (could happen that IBM Cloud has several issue and is not able to handle incoming requests,
         # then it would be probably same for all requests)
        # 502 Bad Gateway (when the CF raises exception, e.g. bad params were provided)
        logger.critical("Unexpected response status from function '%s' in package '%s', status code '%d', response: %s",
                        functionName, package, functionResponse.status_code,
                        json.dumps(functionResponse.json(), ensure_ascii=False).encode('utf8'))
        sys.exit(1)


logger = getScriptLogger(__file__)
