# pylint: disable-msg=W0613, W0612

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
Append the message to one or more bug_tracker issues as note 
and update the SVNRevision field. 
"""


from repoguard.core.module import Handler, ModuleManager
from repoguard.modules.bugtracker import Config


class BugTracker(Handler):
    """
    General bug trackering handler.
    """
    
    __config__ = Config
    
    def __init__(self, transaction):
        """
        Constructor.
        """
        
        Handler.__init__(self, transaction)
        
        self.manager = ModuleManager()

    def _summarize(self, config, protocol):
        """
        Checks valid issue-id and adds a comment to the issue in the bug 
        tracking system.
        
        :param transaction: transaction object
        :param config: Config object
        """
        
        revision = self.transaction.revision
        bugtracker = self.manager.load(self.load_info.name)(config)
        
        issues = bugtracker.parse_msg(self.transaction.commit_msg)
        self.logger.debug("Bug IDs %s found.", ", ".join(issues))
        
        msg = "\n\n".join([entry.msg for entry in protocol])
        
        for issue in issues:
            self.logger.debug("Checking if issue %s exists.", issue)
            if bugtracker.issue_exists(issue):
                bugtracker.add_comment(issue, msg)
                bugtracker.set_revision(issue, revision)
                self.logger.debug("Issue %s finished.", issue)
        self.logger.debug("Bug tracker finished.")
