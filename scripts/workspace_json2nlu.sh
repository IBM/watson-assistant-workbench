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
    echo "Usage: $0 [-h|--help] -w workspace.json -s scriptdir -r resultdir -p prefix"
    if [ -z "$1" ]; then
      echo " -h - print this help message"
    fi
}

PREFIX=""

while [ $# -gt 0 ]; do
    case "$1" in
    -w)
        WORKSPACE=$2;
        shift
        ;;
    -s)
        SCRIPTDIR=$2;
        shift
        ;;
    -r)
        RESULTDIR=$2;
        shift
        ;;
    -p)
        PREFIX=$2;
        shift
        ;;
    -h|--help)
        PrintHelp
        exit 1;
        ;;
    esac
    shift
done

mkdir -p $RESULTDIR/intents
mkdir -p $RESULTDIR/entities

python $SCRIPTDIR/workspace_decompose.py $WORKSPACE -e $RESULTDIR/entities.json -i $RESULTDIR/intents.json -v
python $SCRIPTDIR/intents_json2csv.py $RESULTDIR/intents.json $RESULTDIR/intents -v
python $SCRIPTDIR/entities_json2csv.py $RESULTDIR/entities.json $RESULTDIR/entities -v
if [ -n "$PREFIX" ]
    then
        python $SCRIPTDIR/intents_csv2nlu.py $RESULTDIR/intents $RESULTDIR/training_data.tsv -e $RESULTDIR/entities -p $PREFIX -l $RESULTDIR/intent_list.txt -m $RESULTDIR/domains_intents_mapADD.csv -v
    else
        python $SCRIPTDIR/intents_csv2nlu.py $RESULTDIR/intents $RESULTDIR/training_data.tsv -e $RESULTDIR/entities -l $RESULTDIR/intent_list.txt -m $RESULTDIR/domains_intents_mapADD.csv -v
fi
python $SCRIPTDIR/entities_csv2nlu.py $RESULTDIR/training_data.tsv $RESULTDIR/entities -l $RESULTDIR/entity_list.txt -i $RESULTDIR/intents_entities_mapADD.csv -d $RESULTDIR/domains_entities_mapADD.csv -v

rm $RESULTDIR/entities.json $RESULTDIR/intents.json
