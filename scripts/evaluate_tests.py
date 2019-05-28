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

import deprecation

import workspace_test_evaluate
from _version import __version__

from wawCommons import getScriptLogger, setLoggerConfig

logger = getScriptLogger(__file__)

@deprecation.deprecated(deprecated_in='2.2', removed_in='2.6', current_version=__version__, details='Use the workspace_test_evaluate.py script / main function instead.')
def main(argv):

    parser = argparse.ArgumentParser(description='Compares all dialog flows from given files and generate xml report', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args, unknown = parser.parse_known_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    workspace_test_evaluate.main(argv)

if __name__ == '__main__':
    main(sys.argv[1:])
