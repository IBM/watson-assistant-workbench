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

import pytest
import warnings

# register 'skipiffails' mark to get rid of warning
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "skipiffails(label=None): mark test to run and if it fails then it is skipped and assertion along with label is printed to warnings section"
    )

# custom format of warnings to print just the message
def custom_formatwarning(message, category, filename, lineno, line=''):
    return str(message) + '\n'

warnings.formatwarning = custom_formatwarning

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    result = outcome.get_result()

    skipiffailsMarker = None
    for marker in item.iter_markers():
        if marker.name == 'skipiffails':
            skipiffailsMarker = marker

    # only if test failed and is marked by @pytest.mark.skipiffails(label=<OPTIONAL_LABEL_TO_BE_DISPLAYED>)
    if result.when == 'call' and result.outcome == 'failed' and skipiffailsMarker:
        label = ''
        if hasattr(skipiffailsMarker, 'kwargs') and 'label' in skipiffailsMarker.kwargs:
            label = ' - ' + skipiffailsMarker.kwargs['label']

        warnings.warn(
            '\n' + ('=' * 16) + ' TEMPORARY SKIPPED TEST' + label + ' ' + ('=' * 16) + '\n'
            + str(call.excinfo.getrepr(style='short')))
        result.outcome = 'skipped'
