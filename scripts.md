# Scripts
This file shows how to run scripts to create and upload workspace and how to convert it back to WAW representation.
Part of this pipeline is covered by update_all.py script (see below) Except update_all.py script all scripts are ran from the root directory.


## Convert dialog from T2C xlsx to WAW xml
_You don't have to use this script if you don't have dialog written in T2C format (usually FAQ)_

```
python scripts/dialog_xls2xml.py -x example/en_app/xls/E_EN_master.xlsx -gd "example/en_app/generated/dialogs" -gi "example/en_app/generated/intents" -ge "example/en_app/generated/entities" -v
```

## Convert dialog from WAW xml to WCS json
Converts dialog nodes from .xml format to Watson Conversation Service workspace .json format

```
python scripts/dialog_xml2json.py -dm example/en_app/dialogs/E_EN_welcome.xml -of example/en_app/outputs -od dialog.json -s ../data_spec/dialog_schema.xml -v
```

## Convert entities from csv to WCS json
Converts entity csv files to Watson conversation service .json format

```
python scripts/entities_csv2json.py -ie example/en_app/entities/ -od example/en_app/outputs/ -oe entities.json -s -v
```

## Convert intents from csv to WCS json
Converts intent csv files to Watson conversation service .json format

```
python scripts/intents_csv2json.py -ii example/en_app/intents/ -od example/en_app/outputs/ -oi intents.json -s -v
```

## Compose workspace
Concatenate intents, entities and dialogues files to Watson Conversation Service workspace

```
python scripts/workspace_compose.py -ow workspace.json -od dialog.json -oi intents.json -oe entities.json -of example/en_app/outputs/ -wn "My first workspace" -v
```

## Deploy workspace
Deploys workspace in WCS .json format to Watson Conversation Service

_Before running this script you have to create an example/en\_app/private.cfg file with your WCS credentials (you can use example/en\_app/private.cfg.template file as a template)_

```
python scripts/workspace_deploy.py -of example/en_app/outputs/ -ow workspace.json -c example/en_app/private.cfg -oc example/en_app/private.cfg -v
```

## Test workspace
Tests all dialog flows from given file and save received responses to output file

```
python scripts/workspace_test.py example/en_app/private.cfg example/en_app/tests/test_more_outputs.test example/en_app/outputs/test_more_outputs.out -v
```

## Evaluate tests
Compares all dialog flows from given files and generate xml report

```
python scripts/evaluate_tests.py example/en_app/tests/test_more_outputs.test example/en_app/outputs/test_more_outputs.out -o example/en_app/outputs/test_more_outputs.xml -v
```

## Delete workspace
Deletes workspace from Watson Conversation Service and deletes its workspace id from config file

```
python scripts/workspace_delete.py example/en_app/private.cfg -v
```

## Decompose workspace
Decomposes WCS .json workspace to intents, entities and dialogs files in WCS .json format 

```
python scripts/workspace_decompose.py example/en_app/outputs/workspace.json -i example/en_app/outputs/intentsNew.json -e example/en_app/outputs/entitiesNew.json -d example/en_app/outputs/dialogNew.json -v
```

## Convert intents from WCS json to csv
Converts WCS intents from .json format to csv intent files

_At first you have to create new folder for these intents:_

```
mkdir -p example/en_app/outputs/intents
```

```
python scripts/intents_json2csv.py example/en_app/outputs/intentsNew.json example/en_app/outputs/intents/ -v
```

## Convert entities from WCS json to csv
Converts WCS entities from .json format to csv entity files

_At first you have to create new folder for these entities:_

```
mkdir -p outputs/entities
```

```
python scripts/entities_json2csv.py example/en_app/outputs/entitiesNew.json example/en_app/outputs/entities/ -v
```

## Convert dialog from WCS json to WAW xml
Converts WCS dialogs from .json format to WAW xml dialogs file

_At first you have to create new folder for the dialog:_

```
mkdir -p example/en_app/outputs/dialog
```

```
python scripts/dialog_json2xml.py example/en_app/outputs/dialogNew.json -d example/en_app/outputs/dialog/ -v
```

## Update all
Cleans folders for generated and output files, converts dialogs from T2C and WAW xml format and intents and entities from csv format to WCS .json workspace and deploys it to the Watson Conversation Service (Cleans folders specified in config files as "outputs" and "generated" and runs all scripts from dialog_xls2xml.py to workspace_deploy.py)

_You have to run update\_all script from app directory:_

```
cd example/en_app/
```

_Don't forget to create an example/en\_app/private.cfg file with your WCS credentials (you can use example/en\_app/private.cfg.template file as a template). You will probably need to change paths in your config files to not contain "example/en\_app/" part._

```
python ../../scripts/update_all.py -c common.cfg -c private.cfg
```
