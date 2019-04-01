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

import sys, argparse, os
import wawCommons
from wawCommons import setLoggerConfig, getScriptLogger
from cfgCommons import Cfg
import shutil
import logging


logger = getScriptLogger(__file__)

def main(argv):
    setLoggerConfig()
    logger.info('STARTING: ' + os.path.basename(__file__))
    parser = argparse.ArgumentParser(description='Clean generated directories.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-od', '--common_outputs_directory', required=False, help='directory where the otputs will be stored (outputs is default)')
    parser.add_argument('-oi', '--common_outputs_intents', help='file with output json with all the intents')
    parser.add_argument('-oe', '--common_outputs_entities', help='file with output json with all the entities')
    parser.add_argument('-v','--common_verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('-s', '--common_soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    args = parser.parse_args(argv)
    config = Cfg(args)
    VERBOSE = hasattr(config, 'common_verbose')

    if os.path.exists(config.common_generated_dialogs[0]):
        shutil.rmtree(config.common_generated_dialogs[0])
        if VERBOSE:logger.info('%s does not exist.', config.common_generated_dialogs[0])
    else:
        if VERBOSE:logger.info('%s does not exist.', config.common_generated_dialogs[0])

    if os.path.exists(config.common_generated_intents[0]):
        shutil.rmtree(config.common_generated_intents[0])
        if VERBOSE:logger.info('%s does not exist.', config.common_generated_intents[0])
    else:
        if VERBOSE:logger.info('%s doess not exist.', config.common_generated_intents[0])
    if os.path.exists(config.common_generated_entities[0]):
        shutil.rmtree(config.common_generated_entities[0])
        if VERBOSE:logger.info('%s does not exist.', config.common_generated_entities[0])
    else:
        if VERBOSE:logger.info('Does not exist.')
    if os.path.exists(config.common_outputs_directory):
        shutil.rmtree(config.common_outputs_directory)
        if VERBOSE:logger.info('%s has been removed.', config.common_outputs_directory)
    else:
        if VERBOSE:logger.info('%s does not exist.', config.common_outputs_directory)

    logger.info('FINISHING: ' + os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])