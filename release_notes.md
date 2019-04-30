## Release 1.5.2019 v2.1
Since this release, WAW requires Python 3.5 and it is no longer compatible with Python 2. Last WAW version which supports python 2.7 is the 1.2 one.

### New Features
 - You can now delete, upload and test workspace by specifying its name or regular expression
 - It is possible to replace some values using [workspace_addjson](/scripts/workspace_addjson.py) script
 - There is now an option to set the log level in the CLI
 - `-v` flag now just print more INFO messages (not DEBUG or ERROR)
 - Documentation and tests for actions in the dialog were added

#### Cloud Functions
 - While using cloud functions, it is now possible to use an apikey
 - Script [functions_delete_package](/scripts/functions_delete_package.py) for deleting cf package was added
 - Script [functions_deploy](/scripts/functions_deploy.py) is now able to deploy also CF sequences

#### Testing
 - If you set `exception_if_fail` parameter of script [evaluate_tests](/scripts/evaluate_tests.py) to true, it throws exception, when there are any failed tests detected while evaluating.
 - We are running tests for Python 3 only from now on

## Release 1.4.2019 v1.2
This is the last WAW version which supports python 2.7.

### New Features
 - Support for cloud functions was added for deployment and testing
 - WAW now supports [pattern entities](/doc/WAW_entities_doc.md#patterns) and [contextual entities](/doc/WAW_entities_doc.md#contextual-entities) (csv to json direction only)
 - We employ `logging` module for logging
 - Using [workspace_addjson.py](/scripts/workspace_addjson.py) script you are now able to add custom json structures to specified location in the workspace json
 - It is now possible to deploy workspace by its name (by setting `workspace_name_unique` to true)
 - [Dialog testing script](/scripts/evaluate_tests.py) now outputs `junit.xml` file with test results
 - [requirements.txt](/requirements.txt) and [requirements_dev.txt](/requirements_dev.txt) were added to simplify installation process
 - Sample configuration file was split into three: [common.cfg](/example/en_app/common.cfg) (common project settings), [private.cfg](/example/en_app/private.cfg.template) (filled-in template contains credentials, not to be pushed) and [builg.cfg](/example/en_app/build.cfg) (settings specific for concrete build environment, usually not to be pushed). These are just proposal split, not mandatory.

#### WAW xml format

 - Following node tags were added into [WAW xml format](/data_spec/dialog_schema.xml) `disabled`, `metadata`, `type`, `digress_in`, `digress_out` and `digress_out_slots` tags
 - `event_name` tag was added for handlers
 - `result_variable` tag was added for actions
 - Nodes have new attribute `title`
 - In `goto` structure, there is a new tag `behavior` defaulting to `jump_to`
 - It is possible to add [`scope`](/doc/WAW_dialog_doc.txt) attribute to most of the nodes. Scope can be used for creating customized dialogs from a default one.
 - Output structure was updated accordingly to WA changes to contain `generic` tag

#### T2Cformat
 - [T2C format](/doc/T2C_doc.md) now supports folders in a form of an extra channel
 - Options (buttons) in T2C are translated to a format which is understood by clientv2 (it is not yet compliant with response types)
 - Foldables are supported by T2C. Foldables are texts present in a short and a long form. If client supports their rendering (clentv2 does), user can switch between these two forms by clicking on the text.

### Bug fixes
 - It is now possible to load intents from multiple folders
 - Duplicated entities and empty synonyms are handled correctly without raising an error
 - WAW now exports boolean type values into json as booleans, not as strings
 - Conversion of null values, empty values and more complicated structures from json to xml and back again was fixed to result in the json same as original
 - T2C was fixed to create nodes correctly (https://github.com/IBM/watson-assistant-workbench/pull/41)
 - One can now write HTML in T2C or escaped html to WAW xml and it gets rendered properly by the client
 - Reverse order of imported nodes was fixed and nodes are imported to a specified position, not at the end of a node list
 - String formatting issues were fixed

### WAW CI
 - Nightly builds are set up for `devel` and `master` branches
 - Fork PR builds are enabled
 - Artifactory cleanup takes place on each run
 - CI scripts were rewritten to `pytest`
 - Unit testing is enabled for scripts and will be part of all future features
 - `flake8` tests are now part of the CI process, their results are just informative
 - Python 3.6 was added to CI in `allow_failures` mode
 - Check for back and forth conversion (json2xml + xml2json) was added to CI

### Internal
 - Representation of T2C data now employs objective programming
 - `getFilesAtPath` function now supports pattern matching
 - Code was modernized to get ready for Python 3 and an `absolute_import` was added

### Documentation
Following documentation was added
 - [Intents](/doc/WAW_intents_doc.md) and [entities](/doc/WAW_entities_doc.md) format documentation
 - Documentation for [localization](/doc/WAW_dialog_doc.md#localization)
 - Documentation for [logging](/logging.md)


## Release 18.5.2018 v1.1

### New Features in WAW xml format
 - Employ Travis CI
 - Add support for counterexamples
 - Add GENERIC type of autogenerate node (see 'doc/WAW\_dialog\_doc.txt' for more info)
 - Add built-in special key '::FIRST\_SIBLING' (see 'doc/WAW\_dialog\_doc.txt' for more info)
 - Import tag, autogenerate tag and node tag can be in any order
 - Sort intents and entities

### Bug fixes
 - Fix empty GOTO blocks bug in T2C format
 - Fix of reponse type format for supporting the buttons in T2C
 - Convert only files with .xlsx suffix which do not start with . or with ~

### Documentation
 - Update readme with working examples
