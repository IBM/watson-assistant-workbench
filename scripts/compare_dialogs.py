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

import json, sys, os, os.path, argparse
from deepdiff import DeepDiff
from wawCommons import setLoggerConfig, getScriptLogger
import logging


logger = getScriptLogger(__file__)

try:
    basestring            # Python 2
except NameError:
    basestring = (str, )  # Python 3

def main(argv):
    parser = argparse.ArgumentParser(description='Compares dialog JSON before (input) and after (output) the conversion from JSON to WAW and back to JSON', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('inputDialogFileName', help='file with original dialog JSON')
    parser.add_argument('outputDialogFileName', help='file with output dialog JSON run through WAW scripts')
    # optional arguments
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(argv)

    VERBOSE = args.verbose

    inputpath = args.inputDialogFileName
    outputpath = args.outputDialogFileName

    if not os.path.isfile(inputpath):
        logger.error("Input dialog json '%s' does not exist.", inputpath)
        exit(1)

    if not os.path.isfile(outputpath):
        logger.error("Output dialog json '%s' does not exist.", outputpath)
        exit(1)

    with open(inputpath) as f:
        dialogInputUnsorted = json.load(f)

    with open(outputpath) as g:
        dialogOutputUnsorted = json.load(g)

    result = DeepDiff(dialogInputUnsorted, dialogOutputUnsorted, ignore_order=True).json
    if VERBOSE:
        logger.info("result: %s", json.dumps(result, indent=4))

    if result == '{}':
        logger.info("Dialog JSONs are same.")
        exit(0)
    else:
        logger.info("Dialog JSONs differ.")
        exit(1)

if __name__ == '__main__':
    setLoggerConfig()
    main(sys.argv[1:])

