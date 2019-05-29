## Functions
Workbench also supports various operations with Cloud Functions - deploying, deleting and testing (see `scripts/functions_*`).
Those functions then could be called from Watson Assistant (see [WA documentation](https://cloud.ibm.com/docs/services/assistant?topic=assistant-dialog-actions)).

**CF Example (python):**
```python
def main(args):
    name = args.get("name", "World")
    greeting = "Hello " + name + "!"
    print(greeting)
    return {"greeting": greeting}
```
**Recommendation:** Functions files are typically placed to a separate directory `<app_root>/functions` or directories.

### Deploying
TODO: Few sentences about deploying functions

### Deleting
TODO: Few sentences about deleting functions

### Testing
Testing of functions is separated to 2 scripts - [functions_test.py](/scripts/functions_test.py) and [functions_test_evaluate.py](/scripts/functions_test_evaluate.py).
The first script only runs tests against Cloud Functions environment specified in configuration (see [README.md](/README.md))
and saves returned outputs to output file. The second script then could be used to evaluate returned outputs and save the results.

#### Test script
Script [functions_test.py](/scripts/functions_test.py) takes input json file that represents test cases that should be run against
Cloud Functions and produce output that extends input json file by returned outputs
from CFs.

Inputs and expected outputs can contain string values that starts with `::`
(e.g. `"key": "::valueToBeReplaced1"`) which will be replaced by matching
configuration parameters or by values specified by parameter `replace`
(format `valueToBeReplaced1:replacement1,valueToBeReplaced2:replacement2`)).

**Input json file example (could contain additional keys that will be used in evaluation - they will be skipped):**
```
[
    {
        "name": "test example 1", # OPTIONAL
        "cf_package": "<CLOUD FUNCTIONS PACKAGE NAME>", # OPTIONAL (could be provided directly to script, at least one has to be specified, test level overrides global script one)
        "cf_function": "<CLOUD FUNCTIONS SPECIFIC FUNCTION TO BE TESTED>", # --||--
        "input": <OBJECT> | <@PATH/TO/FILE>, # payload to be send to CF (could be specified as a relative or absolute path to the file that contains json file, e.g. "input": "@inputs/test_example_1.json")
        "outputExpected": <OBJECT> | <@PATH/TO/FILE>, # expected payload to be return from CF (--||--)
    },
    {
        "name": "test example 2",
        ...
          rest of the test definition
        ...
    }
]
```

**Output json file example:**
```
[
    {
        "name": "test example 1",
        ...
          rest of the input test definition
        ...
        "outputReturned": <OBJECT> # returned payload from CF
    },
    {
        "name": "test example 2",
        ...
          rest of the input test definition
        ...
        "outputReturned": <OBJECT> # returned payload from CF
        "error": { # in case an error occurs during the testing
            "type": "<ERROR_TYPE>",
            "message": "<ERROR_MESSAGE>"
        },
        "start": "<START_TIMESTAMP_IN_MILLISECONDS>", # see -t script parameter
        "end": "<END_TIMESTAMP_IN_MILLISECONDS>", # --||--
        "time": "<TIME_IN_MILLISECONDS>" # --||--
    }
]
```

#### Evaluation script
Script [functions_test_evaluate.py](/scripts/functions_test_evaluate.py) takes input json file that represents test output against Cloud
Functions and produces output that extends input json file by results
from evaluation.

**Input json file example (could contain additional keys that were used in testing - they will be skipped):**
```
[
    {
        "name": "test example 1", # OPTIONAL
        "type": "EXACT_MATCH", # OPTIONAL (DEFAULT = EXACT_MATCH, OPTIONS = [EXACT_MATCH])
        "outputExpected": <OBJECT> | <@PATH/TO/FILE>, # expected payload to be return from CF (--||--)
        "outputReturned": <OBJECT> # returned payload from CF
    },
    {
        "name": "test example 2",
        ...
          rest of the test definition
        ...
    }
]
```

**Output json file example:**
```
[
    {
        "name": "test example 1",
        ...
          rest of the input test definition
        ...
        "result": <0 - test passed, 1 - test failed>
        "diff": <OBJECT> # if test passed then "diff" is Null, else contains object that represents differences
    }
]
```

**Output junit xml file example (see -j script parameter):**
```
<?xml version="1.0" encoding="utf-8"?>
<testsuites errors="0" failures="0" tests="1" time="761.0">
	<testsuite errors="0" failures="0" name="<TEST_FILE_NAME>" skipped="0" tests="1" time="761.0" timestamp="2019-05-24 12:20:22.173440">
		<testcase name="<TEST_CASE_NAME>" time="761">
            <!-- 1) If test passes then testcase is empty -->
            <!-- 2) If test fails (result == 1) -->
			<failure message="<DIFF_OBJECT>"/>
            <!-- 3) If test ends with error -->
			<error message="<ERROR_MESSAGE>" type="<ERROR_TYPE>"/>
		</testcase>
	</testsuite>
</testsuites>
```
