#
# Copyright 2008 German Aerospace Center (DLR)
#
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


"""    
Test cases for the BuildBot handler.
"""


from configobj import ConfigObj
import pytest

try:
    from repoguard.handlers.buildbot import BuildBot
    _SKIP = False
except ImportError:
    _SKIP = True

_CONFIG_DEFAULT = """
url=localhost
port=8007
user=admin
password=foo
""".splitlines()
    
    
class TestBuildBot(object):
    
    pytestmark = pytest.mark.skipif("_SKIP")
    
    @classmethod
    def setup_class(cls):
        cls.buildbot = BuildBot(None)
        cls.config = ConfigObj(_CONFIG_DEFAULT)
