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

"""
WAW implement deprecation mechanism using package 'deprecation'.
To deprecete a function (or any other piece of code), see example of code:

    import deprecation
    from _version import __version__

    @deprecation.deprecated(
        deprecated_in='2.2',
        removed_in='2.6',
        current_version=__version__,
        details='Use the function_test.py script / main function with version 2.2 instead (--version 2.2).')
    def main(argv):
        ...

Pytest prints warning and list of tests using deprecated code (__version__ >= deprecated_in).
In case of using unsupported code (__version__ >= removed_in), tests fail.

When tests fail because of unsupported code, unsupported code has to be removed (it is time to remove it)
and tests should be removed or updated to newer version of code (supported version if exists)
- only in case such tests do not already exist.

When changing __version__, it is also necessary to change it in README.md (url
https://img.shields.io/badge/WAW-<__version__>-BLUE.svg)
"""
__version__ = '2.2'
