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
    echo "Tests scripts functionality."
    echo "Usage: $0 [-h|--help] -t scriptstestsdir -d datadir -s scriptsdir"
    if [ -z "$1" ]; then
      echo " -h - print this help message"
    fi
}

PREFIX=""

while [ $# -gt 0 ]; do
    case "$1" in
    -h|--help)
        PrintHelp
        exit 1;
        ;;
    -t)
        TESTSDIR=$2;
        shift
        ;;
    -d)
        DATADIR=$2;
        shift
        ;;
    -s)
        SCRIPTSDIR=$2;
        shift
        ;;
    esac
    shift
done

# dialog_text2code.py
rm -rf $TESTSDIR/outputs
mkdir $TESTSDIR/outputs
echo python $SCRIPTSDIR/dialog_text2code.py $TESTSDIR/data/text2codeExample-en.xml $TESTSDIR/outputs/text2codeResource.json -p"EN-TEST"
python $SCRIPTSDIR/dialog_text2code.py $TESTSDIR/data/text2codeExample-en.xml $TESTSDIR/outputs/text2codeResource.json -p"EN-TEST"
#   output to file
echo $SCRIPTSDIR/dialog_text2code.py $TESTSDIR/data/text2codeExample-en.xml $TESTSDIR/outputs/text2codeResource.json -p"EN-TEST" -o $TESTSDIR/outputs/text2codeOutput-en.xml -v
python $SCRIPTSDIR/dialog_text2code.py $TESTSDIR/data/text2codeExample-en.xml $TESTSDIR/outputs/text2codeResource.json -p"EN-TEST" -o $TESTSDIR/outputs/text2codeOutput-en.xml -v
#   czech
echo python $SCRIPTSDIR/dialog_text2code.py $TESTSDIR/data/text2codeExample-cz.xml $TESTSDIR/outputs/text2codeResource.json -a -p"CZ-TEST" -o $TESTSDIR/outputs/text2codeOutput-cz.xml -v
python $SCRIPTSDIR/dialog_text2code.py $TESTSDIR/data/text2codeExample-cz.xml $TESTSDIR/outputs/text2codeResource.json -a -p"CZ-TEST" -o $TESTSDIR/outputs/text2codeOutput-cz.xml -v
#   TODO: join, inplace and tags xpath

# dialog_code2text.py
echo python $SCRIPTSDIR/dialog_code2text.py $TESTSDIR/data/code2textExample-en.xml $TESTSDIR/data/code2textResource.json -v
python $SCRIPTSDIR/dialog_code2text.py $TESTSDIR/data/code2textExample-en.xml $TESTSDIR/data/code2textResource.json -v
#   output to file
echo python $SCRIPTSDIR/dialog_code2text.py $TESTSDIR/data/code2textExample-en.xml $TESTSDIR/data/code2textResource.json -o $TESTSDIR/outputs/code2textOutput-en.xml -v
python $SCRIPTSDIR/dialog_code2text.py $TESTSDIR/data/code2textExample-en.xml $TESTSDIR/data/code2textResource.json -o $TESTSDIR/outputs/code2textOutput-en.xml -v
#   czech
echo python $SCRIPTSDIR/dialog_code2text.py $TESTSDIR/data/code2textExample-cz.xml $TESTSDIR/data/code2textResource.json -o $TESTSDIR/outputs/code2textOutput-cz.xml -v
python $SCRIPTSDIR/dialog_code2text.py $TESTSDIR/data/code2textExample-cz.xml $TESTSDIR/data/code2textResource.json -o $TESTSDIR/outputs/code2textOutput-cz.xml -v
#   TODO: inplace and tags xpath

# intents_csv2nlu.py
#   with list output and prefix (change intent name for you)
echo python $SCRIPTSDIR/intents_csv2nlu.py $DATADIR/intents/ $TESTSDIR/outputs/intentsTestOutput.tsv -e $DATADIR/entities/ -l $TESTSDIR/outputs/intentsTestList.txt -p "MY Intent" -s -v
python $SCRIPTSDIR/intents_csv2nlu.py $DATADIR/intents/ $TESTSDIR/outputs/intentsTestOutput.tsv -e $DATADIR/entities/ -l $TESTSDIR/outputs/intentsTestList.txt -p "MY Intent" -s -v
#   with intents map gnerated
echo python $SCRIPTSDIR/intents_csv2nlu.py $DATADIR/intents/ $TESTSDIR/outputs/intentsTestOutput.tsv -l $TESTSDIR/outputs/intentsTestList.txt -e $DATADIR/entities/ -m $TESTSDIR/outputs/domainIntentsTestMap.csv -v
python $SCRIPTSDIR/intents_csv2nlu.py $DATADIR/intents/ $TESTSDIR/outputs/intentsTestOutput.tsv -l $TESTSDIR/outputs/intentsTestList.txt -e $DATADIR/entities/ -m $TESTSDIR/outputs/domainIntentsTestMap.csv -v

# entities_csv2nlu.py
echo python $SCRIPTSDIR/entities_csv2nlu.py $TESTSDIR/outputs/intentsTestOutput.tsv $DATADIR/entities/ -l $TESTSDIR/outputs/entitiesTestList.csv -d $TESTSDIR/outputs/domainEntitiesTestMap.csv -i $TESTSDIR/outputs/intentsEntitiesTestMap.csv -v
python $SCRIPTSDIR/entities_csv2nlu.py $TESTSDIR/outputs/intentsTestOutput.tsv $DATADIR/entities/ -l $TESTSDIR/outputs/entitiesTestList.csv -d $TESTSDIR/outputs/domainEntitiesTestMap.csv -i $TESTSDIR/outputs/intentsEntitiesTestMap.csv -v

