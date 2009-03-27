# pylint: disable-msg=F0401
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
Class that handles access to the mantis bug tracker. 
"""


from suds.xsd.sxbasic import Import
from suds.client import Client


class Mantis(object):
    """
    Module for mantis handling.
    """
    
    def __init__(self, config):
        """ 
        Initialize the MantisModule object. 
        """
        
        Import.bind('http://schemas.xmlsoap.org/soap/encoding/')
        
        self.client = Client(config.url)
        self.service = self.client.service
        self.user = config.user
        self.password = config.password
        self.custom_field = config.custom_field

    def issue_exists(self, bug_id):
        """ 
        Return whether a bug exists. 
        """
        
        exists = self.service.mc_issue_exists(self.user, self.password, bug_id)
        return bool(exists)
            
    def get_status(self, bug_id):
        """ 
        Return the status of a bug.
        """
        
        result = self.service.mc_issue_get(self.user, self.password, bug_id)
        return result.status[1]
    
    def get_handler(self, bug_id):
        """
        Return the handler of a bug. 
        """
        
        result = self.service.mc_issue_get(self.user, self.password, bug_id)
        return result.handler.name
    
    def add_comment(self, bug_id, text):
        """
        Adds a note to a bug. 
        """
        
        note = self.client.factory.create('IssueNoteData')
        note.text = text
        self.service.mc_issue_note_add(self.user, self.password, bug_id, note)
        
    def set_revision(self, bug_id, value):
        """ 
        Sets the value of a field. 
        """
        
        result = self.service.mc_issue_get(self.user, self.password, bug_id)
        if hasattr(result, 'custom_fields') and result.custom_fields:
            #If the notes are not set to None a web services error occurs.
            result.notes = None
            for custom_field in result.custom_fields:
                name = result.custom_fields[custom_field].field.name
                if name == self.custom_field:
                    result.custom_fields[custom_field].value = value
                    self.service.mc_issue_update(
                        self.user, self.password, bug_id, result
                    )
                    return
                
        raise ValueError("Unable to set custom field '%s'" % self.custom_field)
            