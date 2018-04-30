#!/bin/bash

# Copyright 2018 IBM Corporation
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -euo pipefail

function PrintHelp {
    if [ -n "$1" ]; then
       echo "Unknown argument \"$1\""
    fi
    echo "From Bluemix conversation service workspace (.json format) creates everything needed by NLU data repository for models building."
    echo "Usage: $0 [-h|--help] -i intentsdir -e entitiesdir -d dialogfile -n workspacename-s scriptdir -o outputworkspace"
    if [ -z "$1" ]; then
      echo " -h - print this help message"
    fi
}

PREFIX=""

while [ $# -gt 0 ]; do
    case "$1" in
    -c)
        CONFIGFILE=$2;
        shift
        ;;
    -i)
        INTENTSDIR=$2;
        shift
        ;;
    -e)
        ENTITIESDIR=$2;
        shift
        ;;
    -d)
        DIALOGFILE=$2;
        shift
        ;;
    -s|scripts)
        SCRIPTDIR=$2;
        shift
        ;;
    --schema)
        SCHEMA=$2;
        shift
        ;;
    -n)
        WORKSPACENAME=$2;
        shift
        ;;
    -o)
        OUTPUTWORKSPACE=$2;
        shift
        ;;
    -h|--help)
        PrintHelp
        exit 1;
        ;;
    esac
    shift
done

TMP="tmp"

rm -rf $TMP
mkdir $TMP
python $SCRIPTDIR/intents_csv2json.py $INTENTSDIR $TMP/intents.json -v
python $SCRIPTDIR/entities_csv2json.py $ENTITIESDIR $TMP/entities.json -v
python $SCRIPTDIR/dialog_xml2json.py $DIALOGFILE -s $SCHEMA > $TMP/dialog.json
python $SCRIPTDIR/workspace_compose.py -n $WORKSPACENAME -i $TMP/intents.json -e $TMP/entities.json -d $TMP/dialog.json $OUTPUTWORKSPACE
python $SCRIPTDIR/workspace_deploy.py $OUTPUTWORKSPACE $CONFIGFILE
rm -rf $TMP