# pylint: disable-msg=C0103
# C0103: Ignoring arguments of the issue_add_note.
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
Some global test settings and methods.
"""


import os
import tempfile

from repoguard.core import constants
from repoguard.core.protocol import Protocol, ProtocolEntry
from repoguard.core.transaction import Transaction


class TestRepository(object):
    """ Implements a local Subversion test repository. """
    
    commit_message = "MANTIS ID 1 MANTIS ID 2"
    
    def __init__(self):
        """ Create svn repository. """    
        
        self.repodir = tempfile.mkdtemp().replace("\\", "/")
        self.chkdir = tempfile.mkdtemp().replace("\\", "/")
        
        os.popen("svnadmin create %s" % self.repodir)
        os.popen("svn co file:///%s \"%s\"" % (self.repodir, self.chkdir))

    def create_default(self):
        """ Creates the default repository content. """
        
        self.add_file("test 1.txt", "content")    
        self.set_property("test 1.txt", "svn:keywords", "Date")
        self.add_file("test.java", "public interface test {\n}\n")
        self.commit(self.commit_message)
        return self.repodir, Transaction(self.repodir, "1")

    def add_file(self, filename, content):
        """ Creates a new file in the repository. """
        
        file_object = open(os.path.join(self.chkdir, filename), "w")
        file_object.write(content)
        file_object.close()
        os.popen("svn add \"%s\"" % os.path.join(self.chkdir, filename))
    
    def set_property(self, filename, keyword, value):
        """ Sets a keywords on a file. """
        
        os.popen("svn propset %s %s \"%s\"" \
                 % (keyword, value, os.path.join(self.chkdir, filename)))

    def commit(self, commit_message=""):
        """ Performs a commit. """
        
        os.popen("svn commit -m \"%s\" %s" % (commit_message, self.chkdir))
        return Transaction(self.repodir, "1")
    
    def create_diretory(self, path):
        """
        Create a directory under the given path.
        
        :param path: Path that has to be created.
        :type path: string
        """
        
        os.mkdir(os.path.join(self.chkdir, path))
        os.popen("svn add \"%s\"" % os.path.join(self.chkdir, path))
    
    
class TestProtocol(Protocol):
    """
    Test protocol class.
    """
    
    def __init__(self):
        """
        Constructor.
        """
        
        Protocol.__init__(self, "test")
        
    def add_entry(self, check="dummy", config=None, 
                  result=constants.SUCCESS, msg=""):
        """ Adds a protocol entry. """
        
        entry = TestProtocolEntry.create(check, config, result, msg)
        self.append(entry)
        
        
class TestProtocolEntry(ProtocolEntry):
    """
    Test protocol entry class.
    """
    
    def __init__(self, check="dummy", config=None, 
                 result=constants.SUCCESS, msg=""):
        """
        Constructor.
        """
        
        ProtocolEntry.__init__(self, check, config, result, msg)
        
    @staticmethod
    def create(check="dummy", config=None, result=constants.SUCCESS, msg=""):
        """ Returns a dummy protocol entry. """
        
        return ProtocolEntry(check, config, result, msg)
        
    @staticmethod
    def success():
        """ Returns a "success" protocol entry. """
         
        return ProtocolEntry("dummy", None, constants.SUCCESS, "")
    
    @staticmethod
    def error():
        """ Retunrs a "failure" protocol entry. """
        
        return ProtocolEntry("dummy", None, constants.ERROR, "")
    

class MantisMock(object):
    """ Simple Mantis mock. """
    
    def __init__(self, _):
        """ Sets mock data. """
        
        self._issues = ["1", "2", "3"]
    
    def extract_issues(self, _):
        """ Always returns C{self._issues}. """
        
        return self._issues
    
    def issue_exists(self, issue):
        """ Checks whether the given issue is in C{self._issues}. """
        
        return issue in self._issues
    
    def issue_add_note(self, _, __):
        """ Does nothing. """
        
        pass