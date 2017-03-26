#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wsgi script for running SaltWebGui.
Is possible to use this script from cli as well with a Python Web Server Gateway Interface (WSGI)
HTTP server like uwsgi, gunicon, apache mod_swgi.

Usage:
    FLASK_APP=./wsgi.py flask run

This way is possible to use flask cli commands and pass other options, like:
    FLASK_APP=./wsgi.py FLASK_DEBUG=1 flask run --port 50001
"""
import sys
import os

project = "saltwebgui"

BASE_DIR = os.path.join(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def virtualenv():
    """Activate the virtualenv"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    activate_this = os.path.join(dir_path, 'venv', "bin/activate_this.py")
    execfile(activate_this, dict(__file__=activate_this))

virtualenv()
from saltwebgui import create_app #pylint: disable=wrong-import-position
application = create_app()


@application.cli.command()
def cov():
    """Runs the unit tests with coverage."""
    print 'Please run the script ./get_coverage.py'

@application.cli.command()
def test():
    """Runs the unit tests."""
    print 'please run python -m unittest discover'
