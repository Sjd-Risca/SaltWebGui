# -*- coding: utf-8 -*-
"""Runs the unit tests with coverage.

Usage:
    python ./get_coverage.py
"""
from StringIO import StringIO
import sys
import os
import unittest
import coverage

TEST_DIR = 'tests'

def virtualenv():
    """Activate the virtualenv"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    activate_this = os.path.join(dir_path, 'venv', "bin/activate_this.py")
    execfile(activate_this, dict(__file__=activate_this))

class Tests(object): #pylint: disable=no-init,too-few-public-methods
    """Class identifying all available tests"""

    def suite(self): #pylint: disable=no-self-use
        """This function stores all the modules to be tested"""
        modules_to_test = []
        test_dir = os.listdir(TEST_DIR)
        for test in test_dir:
            if test.startswith('test') and test.endswith('.py'):
                modules_to_test.append(test.rstrip('.py'))

        all_tests = unittest.TestSuite()
        for module in map(__import__, modules_to_test): #pylint: disable=bad-builtin
            all_tests.addTest(unittest.findTestCases(module))
        return all_tests

BASE_DIR = os.path.join(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
TEST_DIR_PATH = os.path.join(BASE_DIR, TEST_DIR)
sys.path.append(TEST_DIR_PATH)

virtualenv()

COV = coverage.coverage(branch=True,
                        include='saltwebgui/*',
                        omit=['*/config/*'])

COV.start()
print 'running coverage test'
from saltwebgui import create_app #pylint: disable=wrong-import-position
application = create_app()
TEST = Tests()
stream = StringIO()
runner = unittest.TextTestRunner(stream=stream)
result = runner.run(TEST.suite())
COV.stop()
COV.save()
print 'Coverage summary:'
COV.report()
COV.html_report()
