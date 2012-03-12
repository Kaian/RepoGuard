# See the file "LICENSE" for the full license governing this code.


"""
Setup script for the RepoGuard distribution.
"""


from __future__ import with_statement
from distutils.command import clean as _clean
from distutils import core
import os
import subprocess
import shutil
import sys

from distribute_setup import use_setuptools
use_setuptools()
import setuptools


class clean(_clean.clean):
    """ Little clean extension: Cleans up a non-empty build directory. """
    
    def run(self):
        if os.path.exists("build") and not self.dry_run:
            shutil.rmtree("build")
        if os.path.exists("doc/html") and not self.dry_run:
            shutil.rmtree("doc/html")
        if os.path.exists("dist") and not self.dry_run:
            shutil.rmtree("dist")
        if os.path.exists(".coverage") and not self.dry_run:
            os.remove(".coverage")
        if os.path.exists("src/repoguard.egg-info") and not self.dry_run:
            shutil.rmtree("src/repoguard.egg-info")


class _BaseCommandRunner(core.Command):
    """ Base class for encapsulating command line commands. """
    
    user_options = [("command=", None, "Path and name of the command line tool.")]
    
    def run(self):
        self._create_build_dir()
        command = self._create_command()
        self._run_command(command)
        self._perform_post_actions()
    
    @staticmethod
    def _create_build_dir():
        if not os.path.exists("build"):
            os.mkdir("build")

    def _create_command(self):
        pass
    
    def _run_command(self, command):
        if self.verbose:
            print(command)
        subprocess.call(command)
    
    def _perform_post_actions(self):
        pass


class pylint(_BaseCommandRunner):
    """ Runs the pylint command. """

    description = "Runs the pylint command."
    user_options = [("out=", None, "Specifies the output type (html or txt). Default: html")]

    def initialize_options(self):
        self.command = "pylint"
        if sys.platform == "win32":
            self.command += ".bat"
        self.out = "html"
        self.output_file_path = "build/pylint.html"

    def finalize_options(self):
        self.verbose = self.distribution.verbose
        if self.out != "html":
            self.output_file_path = "build/pylint.txt"

    def _create_command(self):
        return (
            "%s --rcfile=dev/pylintrc --output-format=%s src/repoguard test/repoguard_test > %s"
            % (self.command, self.out, self.output_file_path))

    def _perform_post_actions(self):
        if self.out != "html" and sys.platform == "win32":
            with open(self.output_file_path, "rb") as file_object:
                content = file_object.read().replace("\\", "/")
            with open(self.output_file_path, "wb") as file_object:
                file_object.write(content)
                

class test(_BaseCommandRunner):
    """ Runs all unit tests. """
    
    description = "Runs all unit tests using py.test."
    user_options = [
        ("out=", None, "Specifies the output format of the test results." \
         + "Formats: xml, standard out. Default: standard out."),
        ("covout=", None, "Specifies the output format of the coverage report." \
         + "Formats: xml, html.")]

    def initialize_options(self):
        self.command = "py.test"
        if sys.platform == "win32":
            self.command += ".exe"
        self.out = None
        self.covout = None
        self.verbose = False

    def finalize_options(self):
        self.verbose = self.distribution.verbose
        
    def _create_command(self):
        options = " test"
        if self.out == "xml":
            options = "--junitxml=build/xunit.xml test"
        if not self.covout is None:
            options = (
                "--cov=src --cov-config=dev/coveragerc --cov-report=%s %s"
                % (self.covout, options))
        return "%s %s" % (self.command, options)


def _perform_setup():
    _set_pythonpath()
    config_home = _get_config_home()
    console_scripts = _get_console_scripts()
    _run_setup(config_home, console_scripts)
    
def _set_pythonpath():
    python_path = [os.path.realpath(path) for path in ["src", "test"]]
    os.environ["PYTHONPATH"] = os.pathsep.join(python_path)

def _get_config_home():
    win32_config_home = os.path.join(os.path.expanduser("~"), ".repoguard")
    _linux_config_home = "/usr/local/share/repoguard"
    config_home = win32_config_home if sys.platform == "win32" else _linux_config_home
    config_home = os.getenv("REPOGUARD_CONFIG_HOME", config_home)
    return config_home

def _get_console_scripts():
    debug = os.getenv("REPOGUARD_DEBUG")
    console_scripts = "repoguard = repoguard.main:main"
    if debug: # Adds a debug prefix to allow test with new version without de-activating the old one
        console_scripts = "repoguard-debug = repoguard.main:main"
    return console_scripts

def _run_setup(config_home, console_scripts):
    setuptools.setup(
        name="repoguard", 
        version="0.3.0",
        cmdclass={"clean": clean, "test": test, "pylint": pylint},
        description="RepoGuard is a framework for Subversion hook scripts.",
        long_description=("RepoGuard is a framework for Subversion pre-commit hooks " 
            + "in order to implement checks of the to be commited files before they are committed."
            + " For example, you can check for the code style or unit tests. The output of the checks" 
            + " can be send by mail or be written into a file or simply print to the console."),
        author="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
        author_email="Malte.Legenhausen@dlr.de",
        maintainer="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
        maintainer_email="tobias.schlauch@dlr.de",
        license="Apache License Version 2.0",
        url="http://repoguard.tigris.org",
        platform="independent",
        classifiers=[
            "Development Status :: 1 - Pre-Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: POSIX",
            "Programming Language :: Python",
            "Topic :: Software Development",
            "Topic :: Software Development :: Quality Assurance",
            "Topic :: Software Development :: Bug Tracking",
            "Topic :: Software Development :: Version Control",
        ],
        namespace_packages=[
            "repoguard",
            "repoguard.checks",
            "repoguard.handlers",
            "repoguard.modules",
            "repoguard.tools"
        ],
        packages=setuptools.find_packages("src"),
        package_dir={"" : "src"},
        data_files=[
            (config_home, [
                "cfg/repoguard.conf",
                "cfg/logger.conf"
            ]),
            (config_home, [
                "cfg/templates/default.tpl.conf",
                "cfg/templates/python.tpl.conf"
            ])
        ],
        install_requires=[
            "configobj>=4.6.0",
            "setuptools>=0.6"
        ],
        extras_require={
            "dev": [
                "Sphinx>=1.1.3",
                "pylint>=0.18.1",
                "pytest>=2.2.3",
                "pytest-cov>=1.5",
                "coverage.py>=3.5"
            ],
            "pylint": [
                "pylint>=0.18.1"
            ],
            "mantis": [
                "suds-jurko>=0.4.1"
            ],
            "buildbot": [
                "twisted>=8.1.0"
            ]
        },
        entry_points={
            "console_scripts": [
                console_scripts
            ],
            "repoguard.checks": [
                "AccessRights = repoguard.checks.accessrights:AccessRights",
                "ASCIIEncoded = repoguard.checks.asciiencoded:ASCIIEncoded",
                "CaseInsensitiveFilenameClash = repoguard.checks.caseinsensitivefilenameclash:CaseInsensitiveFilenameClash",
                "Checkout = repoguard.checks.checkout:Checkout",
                "Checkstyle = repoguard.checks.checkstyle:Checkstyle",
                "Keywords = repoguard.checks.keywords:Keywords",
                "Log = repoguard.checks.log:Log",
                "Mantis = repoguard.checks.mantis [mantis]",
                "PyLint = repoguard.checks.pylint_:PyLint [pylint]",
                "RejectTabs = repoguard.checks.rejecttabs:RejectTabs",
                "UnitTests = repoguard.checks.unittests:UnitTests",
                "XMLValidator = repoguard.checks.xmlvalidator:XMLValidator"
            ],
            "repoguard.handlers": [
                "Mail = repoguard.handlers.mail:Mail",
                "Console = repoguard.handlers.console:Console",
                "File = repoguard.handlers.file:File",
                "Mantis = repoguard.handlers.mantis:Mantis [mantis]",
                "BuildBot = repoguard.handlers.buildbot:BuildBot [buildbot]",
                "Hudson = repoguard.handlers.hudson:Hudson",
                "ViewVC = repoguard.handlers.viewvc:ViewVC"
            ],
            "repoguard.tools": [
                "Checker = repoguard.tools.checker:Checker",
                "Configuration = repoguard.tools.config:Configuration",
                "Repository = repoguard.tools.repository:Repository"
            ]
        }
    )


if __name__ == "__main__":
    _perform_setup()
