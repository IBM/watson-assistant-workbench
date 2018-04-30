# watson-assistant-workbench
WAW is a toolkit for maintaining Watson Assistant data in github repository.
It aims at 
- structured data-driven approach, with easy diffs visible in GitHub
- easy collaboration among large teams
- improved dialog tree representation resulting in greater readability and easier updates compared to the original WA JSON format
- easy-to-use XML format and tools that make authoring of Watson Conversation workspaces easier using standard text editors
- ability to easily include and combine pieces of dialog together
- full compatibility with the WA JSON workspace format
- easy Continuous Integration - each commit to GitHub runs tests and updates conversation workspace if all succeed
- automatic dialog code generation (go back, abort, etc. - actions needed in each dialog step)
- support for internationalization
- and more :)

It countains a bundle of tools for generating WA workspace from the structure data (and viceversa), testing and uploading (working with the WCS API).

Structure:
 - data # data for generating wa workspace
   - dialog # dialog files in .xml format, more documentation in data_spec folder
   - entities # entity lists (each file represents one entity and each line represents one value followed by semicolon separeted synonyms) plus special file for system entities
   - intents # intent lists (each file represents one intent and each line represents one example of sentence)
 - data_spec
   - dialog_doc.txt # documentation for .xml format of dialog
   - dialog_schema.xml # schema of .xml format of dialog
 - outputs # generated folder with all outputs
 - scripts # scripts for generating, testing and uploading wa workspace
 - tests # test data where each file represents bundle of inputs and expected outputs from wa
 - wcs.cfg.template # template for configuration file 'wcs.cfg' containing wa credentials


Currently supported conversation version is 2017-02-03 except:
- Fuzzy matching, Folders, Digression and Pattern defined entities are not supported.
- A name of a dialog node still has to be unique as it is used as node ID.
- Missing "slot_in_focus" property.
- Slots and are not supported in json to xml conversion scripts.

Scripts use python 2.7

Please install following python modules: configparser, openpyxl, cryptography, unidecode, requests


# generate dialog json:
python scripts/dialog_xml2json.py data/dialog/main.xml outputs/dialog.json -s data_spec/dialog_schema.xml -v

# generate entities json:
python scripts/entities_csv2json.py data/entities/ outputs/entities.json -v

# generate intents json:
python scripts/intents_csv2json.py data/intents/ outputs/intents.json -v

# compose workspace:
python scripts/workspace_compose.py outputs/workspace.json -e outputs/entities.json -d outputs/dialog.json -i outputs/intents.json -v

# deploy workspace:
python scripts/workspace_deploy.py outputs/workspace.json wcs.cfg -v

# test workspace:
python scripts/workspace_test.py wcs.cfg tests/test_more_outputs.test outputs/test_more_outputs.out -v

# evaluate tests:
python scripts/evaluate_tests.py tests/test_more_outputs.test outputs/test_more_outputs.out -v

# delete workspace:
python scripts/workspace_delete.py wcs.cfg -v

# decompose workspace:
python scripts/workspace_decompose.py outputs/workspace.json -i outputs/intents.json -e outputs/entities.json -d outputs/dialog.json -v

# extract intents to csv:
python scripts/intents_json2csv.py outputs/intents.json outputs/intents/ -v

# extract entities to csv:
python scripts/entities_json2csv.py outputs/entities.json outputs/entities -v

# convert dialog from json to xml:
python scripts/dialog_json2xml.py outputs/dialog.json -d outputs/dialog/ -v
