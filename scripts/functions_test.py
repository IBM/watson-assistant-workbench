"""
Copyright 2019 IBM Corporation
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

import argparse
import logging
import sys

import _functions_test_v1
import _functions_test_v2
from wawCommons import getScriptLogger, setLoggerConfig

logger = getScriptLogger(__file__)

def main(argv):
    parser = argparse.ArgumentParser(description='Tests all tests specified in given file against Cloud Functions and save test outputs to output file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version', required=False, help='version of the script', choices=['2.1', '2.2'], default='2.1')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args, unknown = parser.parse_known_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    # remove '--version' parameter and its value from argv
    try:
        argv.remove('--version')
        argv.remove(args.version)
    except ValueError:
        pass  # do nothing!

    if args.version == '2.1':
        _functions_test_v1.main(argv)
    elif args.version == '2.2':
        _functions_test_v2.main(argv)
    else:
        logger.critical('Unknown version: ' + args.version)

if __name__ == '__main__':
    main(sys.argv[1:])
